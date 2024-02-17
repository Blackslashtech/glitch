package captcha

import (
	"context"
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestSolve(t *testing.T) {
	const checks = 1000

	for i := 0; i < checks; i++ {
		challenge, err := GenerateChallenge(3 + i%2)
		require.NoError(t, err)

		solution, err := Solve(context.Background(), challenge.String())
		require.NoError(t, err)

		ok, err := challenge.VerifyResponse(solution)
		require.NoError(t, err)
		require.True(t, ok)
	}
}

func BenchmarkSolve(b *testing.B) {
	b.ReportAllocs()

	for difficulty := 4; difficulty <= 7; difficulty++ {
		b.Run(fmt.Sprintf("difficulty=%d", difficulty), func(b *testing.B) {
			challenges := make([]*Challenge, b.N)
			for i := 0; i < b.N; i++ {
				challenge, err := GenerateChallenge(difficulty)
				require.NoError(b, err)
				challenges[i] = challenge
			}

			b.ResetTimer()

			for i := 0; i < b.N; i++ {
				solution, err := Solve(context.Background(), challenges[i].String())
				require.NoError(b, err)

				ok, err := challenges[i].VerifyResponse(solution)
				require.NoError(b, err)
				require.True(b, ok)
			}
		})
	}
}
