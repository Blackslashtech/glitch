<?php
include("config.php");

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
