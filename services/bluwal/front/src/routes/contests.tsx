import {Contest} from "@/proto/bluwal/bluwal";
import {useAuthContext} from "@/routes/authContext";
import {bluwalServiceClient} from "@/services/contests";
import {Button, Checkbox, FormControlLabel, FormGroup, Grid, Stack, Typography,} from "@mui/material";
import {useEffect, useState} from "react";
import {Link} from "react-router-dom";

export default function ContestsContainer() {
    const {userID} = useAuthContext();
    const [onlyMy, setOnlyMy] = useState(false);
    const [contests, setContests] = useState<Array<Contest>>([]);

    useEffect(() => {
        const wrapper = async () => {
            const response = await bluwalServiceClient.contestList({
                author: onlyMy ? userID : undefined,
            });
            setContests(response.contests);
        };
        void wrapper();
    }, [userID, onlyMy]);

    const handleOnlyMyChange = (
        event: React.ChangeEvent<HTMLInputElement>
    ): void => {
        setOnlyMy(event.target.checked);
    };

    return (
        <>
            <Grid container direction="column" spacing={2} m={1}>
                <Grid item>
                    <Stack direction="row" spacing={2}>
                        <FormGroup>
                            <FormControlLabel
                                control={
                                    <Checkbox checked={onlyMy} onChange={handleOnlyMyChange}/>
                                }
                                label="Show only my contests"
                            />
                        </FormGroup>
                        <Button variant="contained" component={Link} to={"/create"}>
                            Create contest
                        </Button>
                    </Stack>
                </Grid>
                <Grid item>
                    <Grid container direction="column" spacing={2}>
                        {contests.map((contest) => (
                            <Grid item key={contest.id}>
                                <Stack direction="row" spacing={2}>
                                    <Grid item xs={6}>
                                        <Typography>
                                            <strong>{contest.id}</strong> by {contest.author}
                                        </Typography>
                                    </Grid>
                                    <Grid item xs={1}>
                                        <Typography>
                                            {contest.challenges.length} challenges
                                        </Typography>
                                    </Grid>
                                    <Grid item xs={1}>
                                        <Button
                                            variant="contained"
                                            component={Link}
                                            to={`/contests/${contest.id}`}
                                        >
                                            Open
                                        </Button>
                                    </Grid>
                                </Stack>
                            </Grid>
                        ))}
                    </Grid>
                </Grid>
            </Grid>
        </>
    );
}
