import {AppBar, Box, Button, Toolbar, Typography} from "@mui/material";
import {useRef} from "react";
import {Link, Outlet} from "react-router-dom";

export default function Root() {
    const topbarRef = useRef<HTMLElement>(null);

    return (
        <>
            <AppBar position="static" ref={topbarRef}>
                <Toolbar>
                    <Typography>Bluwal</Typography>
                    <Button component={Link} to={"/"} color="inherit">
                        Contests
                    </Button>
                </Toolbar>
            </AppBar>
            <Box sx={{width: "100%", height: "100%"}}>
                <Outlet/>
            </Box>
        </>
    );
}
