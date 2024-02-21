<?php

include("config.php");

if(isset($_SESSION['loggedin'])){
    if($_SESSION["loggedin"] == true){
        header("Location: index.php");
    };
};

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $input_username = $_POST["username"];
    $input_password = $_POST["password"];

    // Prepare a SQL statement to fetch user details
    $sql = "SELECT * FROM users WHERE username = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $input_username);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows == 1) {
        $row = $result->fetch_assoc();
        $hashed_password = $row["password"];
        $permission = $row["permission"];
        $comments = $row["comments"];
        // echo "<p>$hashed_password</p>";
        
        // Verify the hashed password
        if ($input_password == $hashed_password) {
            // Authentication successful
            $_SESSION["loggedin"] = true;
            $_SESSION["username"] = $input_username;
            $_SESSION["permission"] = $permission;
            $_SESSION["comments"] = $comments;
            header("Location: index.php"); // Redirect to a welcome page
            exit();
        } else {
            $error_message = "Invalid username or password";
        }
    } else {
        $error_message = "Invalid username or password";
    }

    // if ($input_username == $valid_username && $input_password == $valid_password) {
    //     // Authentication successful
    //     $_SESSION["loggedin"] = true;
    //     $_SESSION["username"] = $input_username;
    //     header("Location: index.php"); // Redirect to a welcome page
    //     exit();
    // } else {
    //     $error_message = "Invalid username or password";
    // }
}
?>

<html class='w-full h-full overflow-hidden hide-scrollbar' style="background: #000 url('alien-bg.jpg') no-repeat center center fixed; -webkit-background-size: cover; -moz-background-size: cover; -o-background-size: cover; background-size: cover;">

<head>
    <!-- Include your stylesheets and other head elements here -->
    <link rel="stylesheet" type="text/css" href="alien.css">
</head>

<body>
<div id="aliens-layer"></div>
    <script src="static/aliens.js"></script>
<div align="center" class="sortable-item">
    <h2>Login</h2>
    <?php 
        if(isset($error_message)){
            echo "<p>$error_message</p>";
        };
    ?>
    <form method="post" action="login.php">
        <label for="username">Username:</label>
        <input type="text" name="username" id="username" required><br><br>

        <label for="password">Password:</label>
        <input type="password" name="password" id="password" required><br><br>

        <input type="submit" class="button" value="Login">
    </form>
    <p><a href="/register.php" class="button">Need to register?</a><a href="/index.php" class="button">Home</a></p>
</div>
    </div>
</body>
</html>
