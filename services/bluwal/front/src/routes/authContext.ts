import {createContext, useContext} from "react";

type AuthContextType = { userID: string };

export const AuthContext = createContext<AuthContextType | null>(null);

export function useAuthContext(): AuthContextType {
    const ctx = useContext(AuthContext);
    if (!ctx) {
        throw new Error("useAuthContext must be used within AuthContext.Provider");
    }
    return ctx;
}
