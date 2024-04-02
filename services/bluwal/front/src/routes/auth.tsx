import {usePersistentStorageValue} from "@/utils/storage";
import {Box, TextField} from "@mui/material";
import {AuthContext} from "./authContext";

export default function AuthProvider({
                                         children,
                                     }: {
    children: React.ReactNode;
}) {
    const [userID, setUserID] = usePersistentStorageValue<string | null>(
        "userID"
    );

    const handleUserIDChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setUserID(event.target.value);
    };

    if (!userID || userID.length !== 36) {
        return (
            <>
                <Box padding={2}>
                    <TextField
                        label="User ID"
                        variant="outlined"
                        size="small"
                        fullWidth
                        helperText="Enter your user ID (uuid format) to authenticate with the server."
                        onChange={handleUserIDChange}
                    />
                </Box>
            </>
        );
    }

    return (
        <AuthContext.Provider value={{userID}}>{children}</AuthContext.Provider>
    );
}
