package challenges

import (
	"fmt"

	bwpb "bluwal/pkg/proto/bluwal"
)

func Check(challenge *bwpb.Challenge, submission *bwpb.ChallengeSubmitRequest) error {
	switch c := challenge.Challenge.(type) {
	case *bwpb.Challenge_FactorChallenge:
		return checkFactorChallenge(c.FactorChallenge, submission.GetFactorChallengeSubmission())
	default:
		return fmt.Errorf("unknown challenge type: %T", challenge.Challenge)
	}
}
