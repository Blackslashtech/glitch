<?php

include("config.php");

if(isset($_SESSION['loggedin'])){

    if($_SESSION["loggedin"] == false){
        header("Location: login.php");
    } else {
        session_destroy();
        header("Location: login.php");
        exit();
    };
} else {
    header("Location: login.php");
};
?>

<html class='w-full h-full overflow-hidden hide-scrollbar' style="background: #000 url('alien-bg.jpg') no-repeat center center fixed; -webkit-background-size: cover; -moz-background-size: cover; -o-background-size: cover; background-size: cover;">

<head>
    <!-- Include your stylesheets and other head elements here -->
    <link rel="stylesheet" type="text/css" href="alien.css">
</head>

<body>

<div align="center">
    <h2>Logout</h2>
</div>

</body>
</html>
