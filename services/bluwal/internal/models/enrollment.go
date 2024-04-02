package models

import (
	"bluwal/internal/convert"
	bwpb "bluwal/pkg/proto/bluwal"
)

type Enrollment struct {
	ID               string `genji:"id"`
	UserID           string `genji:"user_id"`
	ContestID        string `genji:"contest_id"`
	CurrentState     []int  `genji:"current_state"`
	CurrentChallenge int    `genji:"current_challenge"`
}

func NewEnrollmentFromFilter(filter *bwpb.EnrollmentFilter) *Enrollment {
	return &Enrollment{
		UserID:       filter.UserId,
		ContestID:    filter.ContestId,
		CurrentState: convert.Int32ToInt(filter.CurrentState),
	}
}

func (e *Enrollment) ToFilter() *bwpb.EnrollmentFilter {
	return &bwpb.EnrollmentFilter{
		UserId:       e.UserID,
		ContestId:    e.ContestID,
		CurrentState: convert.IntToInt32(e.CurrentState),
	}
}
