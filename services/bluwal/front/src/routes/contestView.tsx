import {Contest, EnrollmentFilter} from "@/proto/bluwal/bluwal";
import {bluwalServiceClient} from "@/services/contests";
import {Button, Grid, Slider, TextField, Typography} from "@mui/material";
import {useEffect, useState} from "react";
import {useParams} from "react-router-dom";
import {useAuthContext} from "./authContext";

interface Enrollment {
    enrollment: EnrollmentFilter;
    currentChallenge: number;
}

export default function ContestView() {
    const {userID} = useAuthContext();
    const {contestID} = useParams();

    const [contest, setContest] = useState<Contest | undefined>();
    const [enrollment, setEnrollment] = useState<Enrollment | undefined>();
    const [challengeSubmission, setChallengeSubmission] = useState("");

    useEffect(() => {
        const wrapper = async () => {
            const response = await bluwalServiceClient.contestGet({
                id: contestID,
                author: userID,
            });
            setContest(response.contest);
        };
        wrapper();
    }, [contestID, userID]);

    if (!contest) {
        return <div>Loading...</div>;
    }

    const handleEnroll = async () => {
        const response = await bluwalServiceClient.contestEnroll({
            enrollmentFilter: {
                contestId: contestID,
                userId: userID,
                currentState: contest.threshold,
            },
        });
        if (!response.enrollmentFilter) {
            return;
        }
        setEnrollment({
            enrollment: response.enrollmentFilter,
            currentChallenge: 0,
        });
    };

    const handleChallengeSubmit = async () => {
        if (!enrollment) {
            return;
        }
        const parts = challengeSubmission.split(":").map((num) => BigInt(num));
        const response = await bluwalServiceClient.challengeSubmit({
            enrollmentFilter: enrollment.enrollment,
            submission: {
                $case: "factorChallengeSubmission",
                factorChallengeSubmission: {
                    factors: parts.map((part) => part.toString()),
                },
            },
        });
        if (!response.enrollmentFilter) {
            return;
        }

        console.log(response, contest.challenges.length);
        if (response.currentChallenge == contest.challenges.length) {
            const rewardResponse = await bluwalServiceClient.claimReward({
                enrollmentFilter: response.enrollmentFilter,
            });
            setContest({...contest, reward: rewardResponse.reward});
            setEnrollment(undefined);
        } else {
            setEnrollment({
                enrollment: response.enrollmentFilter,
                currentChallenge: response.currentChallenge,
            });
        }
    };

    return (
        <Grid container direction="column" wrap="nowrap" sx={{m: 2}}>
            <Grid item xs={4}>
                <Typography>Contest ID: {contest.id}</Typography>
            </Grid>
            {contest.author && (
                <Grid item xs={4}>
                    <Typography>Author: {contest.author}</Typography>
                </Grid>
            )}
            {contest.reward && (
                <Grid item xs={4}>
                    <Typography>Reward: {contest.reward}</Typography>
                </Grid>
            )}
            <Grid item xs={4}>
                <Typography>Goal:</Typography>
                {contest.goal.map((goal, index) => (
                    <Slider
                        key={index}
                        size="small"
                        value={goal}
                        aria-label={`Goal ${index}`}
                        valueLabelDisplay="auto"
                    />
                ))}
            </Grid>
            <Grid item xs={4}>
                <Typography>Threshold:</Typography>
                {contest.threshold.map((threshold, index) => (
                    <Slider
                        key={index}
                        size="small"
                        value={threshold}
                        aria-label={`Threshold ${index}`}
                        valueLabelDisplay="auto"
                    />
                ))}
            </Grid>
            <Grid item xs={4}>
                <Typography>Challenges:</Typography>
                {contest.challenges.map((challenge, index) => (
                    <Typography key={index}>
                        {challenge.characteristic}:{challenge.delta}:
                        {challenge.challenge?.factorChallenge.n}
                    </Typography>
                ))}
            </Grid>

            {enrollment && (
                <Grid item>
                    <Typography>Next challenge:</Typography>
                    <Typography>
                        {contest.challenges[enrollment.currentChallenge].characteristic}:
                        {contest.challenges[enrollment.currentChallenge].delta}:
                        {
                            contest.challenges[enrollment.currentChallenge].challenge
                                ?.factorChallenge.n
                        }
                    </Typography>
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        label="Submission"
                        helperText="Format: <factor>:<factor>:<factor>"
                        value={challengeSubmission}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                            setChallengeSubmission(e.target.value)
                        }
                    />
                    <Button
                        type="submit"
                        variant="contained"
                        sx={{mt: 3, mb: 2}}
                        onClick={handleChallengeSubmit}
                    >
                        Submit
                    </Button>
                </Grid>
            )}
            {!enrollment && (
                <Button
                    type="submit"
                    variant="contained"
                    sx={{mt: 3, mb: 2}}
                    onClick={handleEnroll}
                >
                    Enroll
                </Button>
            )}
        </Grid>
    );
}
