package models

import (
	"fmt"

	"bluwal/internal/convert"
	bwpb "bluwal/pkg/proto/bluwal"

	"github.com/golang/protobuf/proto"
)

type Contest struct {
	ID     string `genji:"id"`
	Author string `genji:"author"`

	Goal      []int `genji:"goal"`
	Threshold []int `genji:"threshold"`

	Challenges [][]byte `genji:"challenges"`

	Reward string `genji:"reward"`
}

func NewContestFromProto(p *bwpb.Contest) (*Contest, error) {
	challenges := make([][]byte, 0, len(p.Challenges))
	for i, c := range p.Challenges {
		raw, err := proto.Marshal(c)
		if err != nil {
			return nil, fmt.Errorf("marshalling contect %d: %w", i, err)
		}
		challenges = append(challenges, raw)
	}

	return &Contest{
		ID:         p.Id,
		Author:     p.Author,
		Goal:       convert.Int32ToInt(p.Goal),
		Threshold:  convert.Int32ToInt(p.Threshold),
		Challenges: challenges,
		Reward:     p.Reward,
	}, nil
}

func (c *Contest) ToProto() (*bwpb.Contest, error) {
	challenges := make([]*bwpb.Challenge, len(c.Challenges))
	for i, ch := range c.Challenges {
		p := new(bwpb.Challenge)
		if err := proto.Unmarshal(ch, p); err != nil {
			return nil, fmt.Errorf("unmarshalling challenge %d: %w", i, err)
		}
		challenges[i] = p
	}

	return &bwpb.Contest{
		Id:         c.ID,
		Author:     c.Author,
		Goal:       convert.IntToInt32(c.Goal),
		Threshold:  convert.IntToInt32(c.Threshold),
		Challenges: challenges,
		Reward:     c.Reward,
	}, nil
}
