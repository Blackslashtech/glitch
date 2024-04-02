import {Challenge, Contest} from "@/proto/bluwal/bluwal";
import {bluwalServiceClient} from "@/services/contests";
import {Box, Button, Slider, Stack, TextField, Typography,} from "@mui/material";
import {useState} from "react";
import {useNavigate} from "react-router-dom";
import {useAuthContext} from "./authContext";

export default function ContestCreateForm() {
    const navigate = useNavigate();

    const {userID} = useAuthContext();

    const [contest, setContest] = useState<Contest>({
        id: "",
        author: userID,
        goal: [],
        threshold: [],
        challenges: [],
        reward: "",
    });

    const [challenges, setChallenges] = useState<string[]>([]);
    const [error, setError] = useState<string | undefined>();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setContest({...contest, [e.target.name]: e.target.value});
    };

    const handleNewGoal = () => {
        setContest({...contest, goal: [...contest.goal, 0]});
    };

    const handleNewThreshold = () => {
        setContest({...contest, threshold: [...contest.threshold, 0]});
    };

    const handleNewChallenge = () => {
        setChallenges((challenges) => [...challenges, ""]);
    };

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (error) {
            return;
        }

        contest.challenges = challenges.map((challenge) => {
            const parts = challenge.split(":").map((num) => BigInt(num));
            const chal: Challenge = {
                challenge: {
                    $case: "factorChallenge",
                    factorChallenge: {n: parts[2].toString()},
                },
                delta: Number(parts[1]),
                characteristic: Number(parts[0]),
            };
            return chal;
        });
        console.log(contest);

        const wrapper = async () => {
            try {
                const response = await bluwalServiceClient.contestCreate({contest});
                navigate(`/contests/${response.contest?.id}`);
            } catch (err) {
                console.error(err);
            }
        };
        void wrapper();
    };

    const handleGoalChange = (index: number, value: number) => {
        const goal = contest.goal;
        goal[index] = value;
        setContest({...contest, goal});
    };

    const handleThresholdChange = (index: number, value: number) => {
        const threshold = contest.threshold;
        threshold[index] = value;
        setContest({...contest, threshold});
    };

    const handleChallengeChange =
        (index: number) => (e: React.ChangeEvent<HTMLInputElement>) => {
            const value = e.target.value;
            const newChallenges = [...challenges];
            newChallenges[index] = value;
            setChallenges(newChallenges);

            try {
                const parts = value.split(":").map((num) => BigInt(num));
                if (parts.length !== 3) {
                    throw new Error();
                }

                const characteristic = Number(parts[0]);
                if (
                    characteristic < 0 ||
                    characteristic > contest.goal.length ||
                    characteristic > contest.threshold.length
                ) {
                    throw new Error();
                }

                setError(undefined);
            } catch (err) {
                setError("Invalid challenge");
            }
        };

    return (
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{m: 2}}>
            <TextField
                margin="normal"
                required
                fullWidth
                label="Reward"
                name="reward"
                value={contest.reward}
                onChange={handleChange}
            />
            <Stack direction="row" spacing={2}>
                <Button variant="contained" onClick={handleNewGoal}>
                    New goal
                </Button>
                <Button variant="contained" onClick={handleNewThreshold}>
                    New threshold
                </Button>
                <Button variant="contained" onClick={handleNewChallenge}>
                    New challenge
                </Button>
            </Stack>
            <Stack direction="column" spacing={1} sx={{mt: 2}}>
                <Typography>Goals</Typography>
                {contest.goal.map((num: number, index: number) => (
                    <Slider
                        key={index}
                        size="small"
                        value={num}
                        onChange={(_, value) => handleGoalChange(index, value as number)}
                        aria-label={`Goal ${index}`}
                        valueLabelDisplay="auto"
                        max={80}
                    />
                ))}
            </Stack>
            <Stack direction="column" spacing={1} sx={{mt: 2}}>
                <Typography>Threshold</Typography>
                {contest.threshold.map((num: number, index: number) => (
                    <Slider
                        key={index}
                        size="small"
                        value={num}
                        onChange={(_, value) =>
                            handleThresholdChange(index, value as number)
                        }
                        aria-label={`Threshold ${index}`}
                        valueLabelDisplay="auto"
                        max={80}
                    />
                ))}
            </Stack>
            <Stack direction="column" spacing={1} sx={{mt: 2}}>
                <Typography>Challenges</Typography>
                {challenges.map((challenge: string, index: number) => (
                    <TextField
                        key={index}
                        margin="normal"
                        required
                        fullWidth
                        label="Factor challenge"
                        helperText="Format: <characteristic>:<delta>:<n>"
                        value={challenge}
                        onChange={handleChallengeChange(index)}
                    />
                ))}
            </Stack>
            {error && <Typography color="error">{error}</Typography>}
            <Button type="submit" fullWidth variant="contained" sx={{mt: 3, mb: 2}}>
                Create Contest
            </Button>
        </Box>
    );
}
