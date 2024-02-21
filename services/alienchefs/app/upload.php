<?php

include("config.php");


if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if(isset($_SESSION['loggedin'])){
        if($_SESSION["loggedin"] != true){  // If not logged in, can't upload recipes
            header('Location: /upload.php?err=Not%20Logged%20in');
        };
        } else {
            header('Location: /upload.php?err=Not%20Logged%20in');
    };
    $title = $_POST["title"];
    $ingredients = $_POST["ingredients"];
    $instructions = $_POST["instructions"];
    $owner = $_SESSION['username'];
    
    // Check if file was uploaded without errors
    if(isset($_FILES["image"]) && $_FILES["image"]["error"] == 0){
        $image = file_get_contents($_FILES["image"]["tmp_name"]);
        $image = bin2hex($image);
    } else {
        echo "Error: " . $_FILES["image"]["error"];
    }
    
    $stmt = $conn->prepare("INSERT INTO recipes (title, ingredients, instructions, owner, image) VALUES (?, ?, ?, ?, ?)");
    $null = NULL;
    $stmt->bind_param("ssssb", $title, $ingredients, $instructions, $owner, $null);
    $stmt->send_long_data(3, $image);

    if ($stmt->execute()) {
        echo '<div class="alien-error">New record created successfull!</div>';
    } else {
        echo '<div class="alien-error">Error: ' . $sql . "</div>" . $conn->error;
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html class='w-full h-full overflow-hidden hide-scrollbar' style="background: #000 url('alien-bg.jpg') no-repeat center center fixed; -webkit-background-size: cover; -moz-background-size: cover; -o-background-size: cover; background-size: cover;">

<head>
    <!-- Include your stylesheets and other head elements here -->
    <link rel="stylesheet" type="text/css" href="alien.css">
</head>
<html>
<body>
<div id="aliens-layer"></div>
    <script src="static/aliens.js"></script>
<div class="sortable-item">
<h2 class="text-3xl leading-9 font-extrabold tracking-tight sm:text-4xl sm:leading-10 sortable-item">Upload Recipe</h2>
<p>Note you must be registered and logged in to upload recipes</p>
<?php if(isset($_GET['err'])){
    echo '<div class="alien-error">' . $_GET['err'] . '</div>';
} ?>

<form action="upload.php" method="post" enctype="multipart/form-data">
  <label for="title">Title:</label><br>
  <input type="text" id="title" name="title"><br>
  <label for="ingredients">Ingredients:</label><br>
  <textarea id="ingredients" name="ingredients" rows="4" type="text" cols="50"></textarea><br>
  <label for="instructions">Instructions:</label><br>
  <textarea id="instructions" name="instructions" rows="4" type="text" cols="50"></textarea><br>
  <label for="image">Select image:</label>
  <input type="file" class="button" id="image" name="image"><br><br>
  <input type="submit" class="button" value="Upload Recipe">
</form>

<p><a href="/index.php" class="button">Go to Home Page</a></p>
</div>
</div>
</body>
</html>
