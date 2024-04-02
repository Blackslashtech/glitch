package convert

import (
	"github.com/samber/lo"
)

func Int32ToInt(a []int32) []int {
	return lo.Map(a, func(item int32, _ int) int {
		return int(item)
	})
}

func IntToInt32(a []int) []int32 {
	return lo.Map(a, func(item int, _ int) int32 {
		return int32(item)
	})
}
