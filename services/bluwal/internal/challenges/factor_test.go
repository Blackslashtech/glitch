package challenges

import (
	"strings"
	"testing"

	bwpb "bluwal/pkg/proto/bluwal"
)

func Test_checkFactorChallenge(t *testing.T) {
	tests := []struct {
		name       string
		challenge  string
		submission string

		wantErr bool
	}{
		{
			name:       "simple",
			challenge:  "143",
			submission: "11,13",
			wantErr:    false,
		},
		{
			name:       "error",
			challenge:  "144",
			submission: "11,13",
			wantErr:    true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if err := checkFactorChallenge(
				&bwpb.FactorChallenge{N: tt.challenge},
				&bwpb.FactorChallengeSubmission{Factors: strings.Split(
					tt.submission,
					",",
				)},
			); (err != nil) != tt.wantErr {
				t.Errorf("checkFactorChallenge() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}
