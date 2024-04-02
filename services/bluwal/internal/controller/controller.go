package controller

import (
	"errors"
	"fmt"

	"bluwal/internal/models"

	"github.com/genjidb/genji"
	"github.com/genjidb/genji/document"
	"github.com/genjidb/genji/types"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

var (
	ErrEnrollmentNotComplete = errors.New("enrollment is not complete")
)

type Controller struct {
	db *genji.DB
}

func NewController(db *genji.DB) (*Controller, error) {
	c := &Controller{
		db: db,
	}
	if err := c.migrate(); err != nil {
		return nil, fmt.Errorf("migrating: %w", err)
	}
	return c, nil
}

func (c *Controller) CreateContest(contest *models.Contest) error {
	if err := c.db.Exec("INSERT INTO contests VALUES ?", contest); err != nil {
		return fmt.Errorf("inserting into db: %w", err)
	}
	return nil
}

func (c *Controller) GetContest(id string) (*models.Contest, error) {
	var contest models.Contest
	doc, err := c.db.QueryDocument("SELECT * FROM contests WHERE id = ?", id)
	if err != nil {
		return nil, fmt.Errorf("querying contest: %w", err)
	}
	if err := document.StructScan(doc, &contest); err != nil {
		return nil, fmt.Errorf("scanning contest: %w", err)
	}
	return &contest, nil
}

func (c *Controller) ListContests(author string, limit, offset uint32) ([]*models.Contest, error) {
	var (
		err error
		res *genji.Result
	)
	if author == "" {
		res, err = c.db.Query("SELECT * FROM contests LIMIT ? OFFSET ?", limit, offset)
	} else {
		res, err = c.db.Query("SELECT * FROM contests WHERE author = ? LIMIT ? OFFSET ?", author, limit, offset)
	}
	if err != nil {
		return nil, fmt.Errorf("querying contests: %w", err)
	}
	defer func() {
		if err := res.Close(); err != nil {
			logrus.Errorf("closing result: %v", err)
		}
	}()

	var contests []*models.Contest
	if err := res.Iterate(func(d types.Document) error {
		var contest models.Contest
		if err := document.StructScan(d, &contest); err != nil {
			return fmt.Errorf("scanning contest: %w", err)
		}
		contests = append(contests, &contest)
		return nil
	}); err != nil {
		return nil, fmt.Errorf("iterating contests: %w", err)
	}

	return contests, nil
}

func (c *Controller) CreateEnrollment(enrollment *models.Enrollment) error {
	enrollment.ID = uuid.NewString()
	if err := c.db.Exec("INSERT INTO enrollments VALUES ?", enrollment); err != nil {
		return fmt.Errorf("inserting into db: %w", err)
	}
	return nil
}

func (c *Controller) UpdateEnrollment(filter, enrollment *models.Enrollment) error {
	if err := c.db.Exec(
		`
		UPDATE enrollments 
		SET 
			current_challenge = ?, 
			current_state = ? 
		WHERE 
			user_id = ? AND 
			contest_id = ? AND 
			current_state = ?
		`,
		enrollment.CurrentChallenge,
		enrollment.CurrentState,
		filter.UserID,
		filter.ContestID,
		filter.CurrentState,
	); err != nil {
		return fmt.Errorf("updating enrollment: %w", err)
	}
	return nil
}

func (c *Controller) GetEnrollment(filter *models.Enrollment) (*models.Enrollment, error) {
	var enrollment models.Enrollment
	doc, err := c.db.QueryDocument(
		"SELECT * FROM enrollments WHERE user_id = ? AND contest_id = ? AND current_state = ?",
		filter.UserID,
		filter.ContestID,
		filter.CurrentState,
	)
	if err != nil {
		return nil, fmt.Errorf("querying enrollment: %w", err)
	}
	if err := document.StructScan(doc, &enrollment); err != nil {
		return nil, fmt.Errorf("scanning enrollment: %w", err)
	}
	return &enrollment, nil
}

func (c *Controller) CheckEnrollmentComplete(filter *models.Enrollment) error {
	contest, err := c.GetContest(filter.ContestID)
	if err != nil {
		return fmt.Errorf("getting contest: %w", err)
	}

	doc, err := c.db.QueryDocument(
		"SELECT count(*) FROM enrollments WHERE user_id = ? AND contest_id = ? AND current_state >= ?",
		filter.UserID,
		filter.ContestID,
		contest.Goal,
	)
	if err != nil {
		return fmt.Errorf("querying enrollments: %w", err)
	}

	var cnt int
	if err := document.Scan(doc, &cnt); err != nil {
		return fmt.Errorf("scanning contest count: %w", err)
	}
	if cnt == 0 {
		return ErrEnrollmentNotComplete
	}
	return nil
}

func (c *Controller) migrate() error {
	if err := c.db.Exec(
		`CREATE TABLE IF NOT EXISTS contests (
				id TEXT PRIMARY KEY,
				author TEXT NOT NULL,
				reward TEXT NOT NULL,
				...
		)`,
	); err != nil {
		return fmt.Errorf("creating contests table: %w", err)
	}

	if err := c.db.Exec(
		`CREATE TABLE IF NOT EXISTS enrollments (
				id TEXT PRIMARY KEY NOT NULL,
				user_id TEXT NOT NULL,
				contest_id TEXT NOT NULL,
				current_state ARRAY NOT NULL,
				...
		);
		
		-- imagine if genji supported composite primary keys.
		CREATE INDEX IF NOT EXISTS idx_enrollments_pk ON enrollments(user_id, contest_id, current_state);
		`,
	); err != nil {
		return fmt.Errorf("creating enrollments table: %w", err)
	}

	return nil
}
