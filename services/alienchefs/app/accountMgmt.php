<?php
include("config.php");


if(isset($_SESSION['permission'])){
    if($_SESSION["permission"] != 'admin'){
        header("Location: index.php?msg=Must be an admin!");
    };
} else {
    header("Location: index.php?msg=Must be an admin!");
};

if(isset($_POST['id']) && isset($_POST['newpass'])){
    $newpass = $_POST['newpass'];
    $userid = $_POST['id'];
    $stmt = $conn->prepare("UPDATE password FROM recipes WHERE id = ". $id);

}

$id = $_GET['id']; // Assuming you pass the image ID as a GET parameter

// Prepare the SQL statement
$stmt = $conn->prepare("SELECT image FROM recipes WHERE id = ". $id);

// Execute the query
$stmt->execute();

// Bind the result
$stmt->bind_result($image);
$stmt->fetch();

// Set the content-type header to display the image
header("Content-Type: image/jpeg"); // Change 'image/jpeg' to the correct image MIME type if necessary

echo hex2bin($image);

$stmt->close();
$conn->close();
?>
