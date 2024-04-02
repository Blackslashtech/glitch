package service

import (
	"context"
	"errors"
	"slices"

	"bluwal/internal/challenges"
	"bluwal/internal/controller"
	"bluwal/internal/convert"
	"bluwal/internal/models"
	bwpb "bluwal/pkg/proto/bluwal"

	"github.com/google/uuid"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type Service struct {
	bwpb.UnimplementedBluwalServiceServer

	c *controller.Controller
}

func NewService(c *controller.Controller) *Service {
	return &Service{
		c: c,
	}
}

func (s *Service) ContestCreate(_ context.Context, request *bwpb.ContestCreateRequest) (*bwpb.ContestCreateResponse, error) {
	if request.Contest == nil {
		return nil, status.Errorf(codes.InvalidArgument, "contest must be set")
	}
	if len(request.Contest.Threshold) == 0 {
		return nil, status.Errorf(codes.InvalidArgument, "threshold must be set")
	}
	if len(request.Contest.Goal) == 0 {
		return nil, status.Errorf(codes.InvalidArgument, "goal must be set")
	}
	if len(request.Contest.Challenges) == 0 {
		return nil, status.Errorf(codes.InvalidArgument, "challenges must be set")
	}
	if request.Contest.Reward == "" {
		return nil, status.Errorf(codes.InvalidArgument, "reward must be set")
	}
	for _, chal := range request.Contest.Challenges {
		if chal == nil {
			return nil, status.Errorf(codes.InvalidArgument, "challenges must be set")
		}
		if chal.Characteristic < 0 {
			return nil, status.Errorf(codes.InvalidArgument, "characteristic must be set")
		}
	}
	request.Contest.Id = uuid.NewString()

	contest, err := models.NewContestFromProto(request.Contest)
	if err != nil {
		return nil, status.Errorf(codes.InvalidArgument, "invalid contest: %v", err)
	}
	if err := s.c.CreateContest(contest); err != nil {
		return nil, status.Errorf(codes.Internal, "creating contest: %v", err)
	}

	res, err := contest.ToProto()
	if err != nil {
		return nil, status.Errorf(codes.Internal, "marshalling contest: %v", err)
	}
	return &bwpb.ContestCreateResponse{
		Contest: res,
	}, nil
}

func (s *Service) ContestGet(_ context.Context, request *bwpb.ContestGetRequest) (*bwpb.ContestGetResponse, error) {
	if request.Id == "" {
		return nil, status.Errorf(codes.InvalidArgument, "id must be set")
	}

	contest, err := s.c.GetContest(request.Id)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "getting contest: %v", err)
	}

	if contest.Author != request.Author {
		contest.Reward = ""
		contest.Author = ""
	}

	res, err := contest.ToProto()
	if err != nil {
		return nil, status.Errorf(codes.Internal, "marshalling contest: %v", err)
	}
	return &bwpb.ContestGetResponse{
		Contest: res,
	}, nil
}

func (s *Service) ContestList(_ context.Context, request *bwpb.ContestListRequest) (*bwpb.ContestListResponse, error) {
	if request.Limit == 0 {
		request.Limit = 20
	}
	if request.Limit > 50 {
		request.Limit = 50
	}
	contests, err := s.c.ListContests(request.Author, request.Limit, request.Offset)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "listing contests: %v", err)
	}

	contestsProto := make([]*bwpb.Contest, 0, len(contests))
	for _, contest := range contests {
		contest.Author = ""
		contest.Reward = ""
		contestProto, err := contest.ToProto()
		if err != nil {
			return nil, status.Errorf(codes.Internal, "converting contest to proto: %v", err)
		}
		contestsProto = append(contestsProto, contestProto)
	}
	return &bwpb.ContestListResponse{
		Contests: contestsProto,
	}, nil
}

func (s *Service) ContestEnroll(_ context.Context, request *bwpb.ContestEnrollRequest) (*bwpb.ContestEnrollResponse, error) {
	if request.EnrollmentFilter == nil {
		return nil, status.Errorf(codes.InvalidArgument, "enrollment_filter must be set")
	}
	if request.EnrollmentFilter.ContestId == "" {
		return nil, status.Errorf(codes.InvalidArgument, "enrollment_filter.contest_id must be set")
	}
	if request.EnrollmentFilter.UserId == "" {
		return nil, status.Errorf(codes.InvalidArgument, "enrollment_filter.user_id must be set")
	}
	if len(request.EnrollmentFilter.CurrentState) == 0 {
		return nil, status.Errorf(codes.InvalidArgument, "enrollment_filter.current_state must be set")
	}

	contest, err := s.c.GetContest(request.EnrollmentFilter.ContestId)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "getting contest: %v", err)
	}

	enrollment := models.NewEnrollmentFromFilter(request.EnrollmentFilter)
	if slices.Compare(contest.Goal, enrollment.CurrentState) <= 0 {
		return nil, status.Errorf(codes.FailedPrecondition, "you are too good already")
	}
	if slices.Compare(contest.Threshold, enrollment.CurrentState) > 0 {
		return nil, status.Errorf(codes.FailedPrecondition, "lol, noob")
	}

	if err := s.c.CreateEnrollment(enrollment); err != nil {
		return nil, status.Errorf(codes.Internal, "creating enrollment: %v", err)
	}

	return &bwpb.ContestEnrollResponse{
		EnrollmentFilter: enrollment.ToFilter(),
	}, nil
}

func (s *Service) ChallengeSubmit(_ context.Context, request *bwpb.ChallengeSubmitRequest) (*bwpb.ChallengeSubmitResponse, error) {
	if request.EnrollmentFilter == nil {
		return nil, status.Errorf(codes.InvalidArgument, "enrollment_filter must be set")
	}

	contest, err := s.c.GetContest(request.EnrollmentFilter.ContestId)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "getting contest: %v", err)
	}
	contestProto, err := contest.ToProto()
	if err != nil {
		return nil, status.Errorf(codes.Internal, "marshalling contest: %v", err)
	}

	enrollmentFilter := models.NewEnrollmentFromFilter(request.EnrollmentFilter)
	enrollment, err := s.c.GetEnrollment(enrollmentFilter)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "getting enrollment: %v", err)
	}

	if enrollment.CurrentChallenge >= len(contest.Challenges) {
		return nil, status.Errorf(codes.InvalidArgument, "no more challenges")
	}

	challenge := contestProto.Challenges[enrollment.CurrentChallenge]

	if int(challenge.Characteristic) >= len(enrollment.CurrentState) {
		return nil, status.Errorf(codes.InvalidArgument, "invalid characteristic")
	}

	if err := challenges.Check(challenge, request); err != nil {
		return nil, status.Errorf(codes.InvalidArgument, "invalid submission: %v", err)
	}

	enrollment.CurrentChallenge++
	enrollment.CurrentState[int(challenge.Characteristic)] += int(challenge.Delta)
	if err := s.c.UpdateEnrollment(enrollmentFilter, enrollment); err != nil {
		return nil, status.Errorf(codes.Internal, "updating enrollment: %v", err)
	}

	return &bwpb.ChallengeSubmitResponse{
		EnrollmentFilter: enrollment.ToFilter(),
		CurrentChallenge: int32(enrollment.CurrentChallenge),
	}, nil
}

func (s *Service) CheckGoal(_ context.Context, request *bwpb.CheckGoalRequest) (*bwpb.CheckGoalResponse, error) {
	if request.EnrollmentFilter == nil {
		return nil, status.Errorf(codes.InvalidArgument, "enrollment_filter must be set")
	}

	enrollment, err := s.c.GetEnrollment(models.NewEnrollmentFromFilter(request.EnrollmentFilter))
	if err != nil {
		return nil, status.Errorf(codes.Internal, "getting enrollment: %v", err)
	}

	return &bwpb.CheckGoalResponse{
		CurrentChallenge: int32(enrollment.CurrentChallenge),
		CurrentState:     convert.IntToInt32(enrollment.CurrentState),
	}, nil
}

func (s *Service) ClaimReward(_ context.Context, request *bwpb.ClaimRewardRequest) (*bwpb.ClaimRewardResponse, error) {
	if request.EnrollmentFilter == nil {
		return nil, status.Errorf(codes.InvalidArgument, "enrollment_filter must be set")
	}

	if err := s.c.CheckEnrollmentComplete(models.NewEnrollmentFromFilter(request.EnrollmentFilter)); err != nil {
		if errors.Is(err, controller.ErrEnrollmentNotComplete) {
			return nil, status.Errorf(codes.FailedPrecondition, "enrollment not complete")
		}
		return nil, status.Errorf(codes.Internal, "enrollment not complete: %v", err)
	}

	contest, err := s.c.GetContest(request.EnrollmentFilter.ContestId)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "getting contest: %v", err)
	}

	return &bwpb.ClaimRewardResponse{
		Reward: contest.Reward,
	}, nil
}
