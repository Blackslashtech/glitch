import "@/index.css";
import AuthProvider from "@/routes/auth";
import Root from "@/routes/root";
import theme from "@/theme";
import {ThemeProvider} from "@emotion/react";
import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";
import React from "react";
import ReactDOM from "react-dom/client";
import {createBrowserRouter, RouterProvider} from "react-router-dom";
import ContestCreateContainer from "./routes/contestCreate";
import ContestsContainer from "./routes/contests";
import ContestView from "./routes/contestView";

const router = createBrowserRouter([
    {
        path: "/",
        element: <Root/>,
        children: [
            {
                index: true,
                element: (
                    <AuthProvider>
                        <ContestsContainer/>
                    </AuthProvider>
                ),
            },
            {
                path: "/create",
                element: (
                    <AuthProvider>
                        <ContestCreateContainer/>
                    </AuthProvider>
                ),
            },
            {
                path: "/contests/:contestID",
                element: (
                    <AuthProvider>
                        <ContestView/>
                    </AuthProvider>
                ),
            },
        ],
    },
]);

// eslint-disable-next-line @typescript-eslint/no-non-null-assertion
ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
        <ThemeProvider theme={theme}>
            <RouterProvider router={router}/>
        </ThemeProvider>
    </React.StrictMode>
);
