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
    if(isset($_POST['permission'])){
        $input_permission = $_POST['permission'];
    } else {
        $input_permission = 'user';
    };
    if(isset($_POST['comments'])){
        $comments = $_POST['comments'];
    } else {
        $comments = '';
    };

    // Prepare a SQL statement to fetch user details
    $sql = "SELECT * FROM users WHERE username = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $input_username);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows >= 1) {
        $error = 'Username already exists!';
        header("Location: register.php?msg=" . $error);
        exit();
    } else {
        $sql = "INSERT INTO users (username, password, comments, permission) VALUES ('$input_username', '$input_password', '$comments', '$input_permission')";
        $stmt = $conn->prepare($sql);
        // $stmt->bind_param("s", $input_username);
        $stmt->execute();
        $create_result = $stmt->get_result();
        header("Location: register.php?msg=Created user " . $input_username . "!");
        exit();
        } 
    };

    // if ($input_username == $valid_username && $input_password == $valid_password) {
    //     // Authentication successful
    //     $_SESSION["loggedin"] = true;
    //     $_SESSION["username"] = $input_username;
    //     header("Location: index.php"); // Redirect to a welcome page
    //     exit();
    // } else {
    //     $error_message = "Invalid username or password";
    // }
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
    <h2>Register</h2>
    <?php 
        if(isset($_GET['msg'])){
            echo '<div class="alien-error">' . $_GET['msg'] . '</div>';
        };
    ?>
    <form method="post" action="register.php">
        <label for="username">Username:</label>
        <input type="text" name="username" id="username" required><br><br>

        <label for="password">Password:</label>
        <input type="password" name="password" id="password" required><br><br>

        <label for="comments">Comments:</label>
        <input type="text" name="comments" id="comments" ><br><br>

        <input type="submit" class="button" value="Register">
    </form>
    <p><a href="/login.php" class="button">Want to login?</a><a href="/index.php" class="button">Home</a></p>
</div>
    </div>
</body>
</html>
