package challenges

import (
	"fmt"
	"math/big"

	bwpb "bluwal/pkg/proto/bluwal"
)

func checkFactorChallenge(challenge *bwpb.FactorChallenge, submission *bwpb.FactorChallengeSubmission) error {
	if submission == nil {
		return fmt.Errorf("missing factor challenge submission")
	}

	n, ok := new(big.Int).SetString(challenge.N, 10)
	if !ok {
		return fmt.Errorf("invalid n: %s", challenge.N)
	}

	if len(submission.Factors) == 0 {
		return fmt.Errorf("invalid number of factors: %d", len(submission.Factors))
	}

	factors := make([]*big.Int, len(submission.Factors))
	for i, f := range submission.Factors {
		factors[i], ok = new(big.Int).SetString(f, 10)
		if !ok {
			return fmt.Errorf("invalid factor %d: %s", i, f)
		}
		if factors[i].Cmp(big.NewInt(1)) <= 0 {
			return fmt.Errorf("invalid factor %d: %s", i, f)
		}
		if factors[i].Cmp(n) >= 0 {
			return fmt.Errorf("invalid factor %d: %s", i, f)
		}
	}

	res := factors[0]
	if len(factors) > 1 {
		for _, f := range factors[1:] {
			res.Mul(res, f)
			if res.Cmp(n) >= 0 {
				break
			}
		}
	}
	if res.Cmp(n) != 0 {
		return fmt.Errorf("invalid factors: %v", submission.Factors)
	}

	return nil
}
