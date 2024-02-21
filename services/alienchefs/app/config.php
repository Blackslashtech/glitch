<?php

session_start();

$servername = "db";
$username = "user";
$password = "password";
$dbname = "alienchefs_db";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Function to fetch recipes from the database
function getRecipesFromDatabase() {
    global $conn;

    $recipes = array();

    // Assuming you have a 'recipes' table with 'image' and 'title' columns
    $sql = "SELECT id, image, title, ingredients, instructions, owner FROM recipes";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) {
            $recipes[] = $row;
        };
    }

    return $recipes;
}

function getSingleRecipe($id) {
    global $conn;

    $recipes = array();

    // Assuming you have a 'recipes' table with 'image' and 'title' columns
    $sql = "SELECT id, image, title, ingredients, instructions, owner FROM recipes WHERE id = '$id'";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) {
            $recipes[] = $row;
        }
    }

    return $recipes;
}

function getRandomRecipes($numRecords = 5) {
    global $conn;

    // SQL query to fetch five random rows from the 'recipes' table
    $sql = "SELECT * FROM recipes ORDER BY RAND() LIMIT " . $numRecords;

    // Execute the query
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) {
            $recipes[] = $row;
        }
    }

    return $recipes;
}

function getCountRecipes() {
    global $conn;

    // SQL query to count records in the "recipes" table
    $sql = "SELECT COUNT(*) as count FROM recipes";

    // Execute the query
    $result = $conn->query($sql);

    // Check if the query was successful
    if ($result) {
        // Fetch the result as an associative array
        $row = $result->fetch_assoc();

        // Get the count of records
        $recordCount = $row["count"];

        // Output the count
        return number_format($recordCount);

    } else {
        echo "Error executing the query: " . $conn->error;
    }
}

function getCountUsers() {
    global $conn;

    // SQL query to count records in the "users" table
    $sql = "SELECT COUNT(*) as count FROM users";

    // Execute the query
    $result = $conn->query($sql);

    // Check if the query was successful
    if ($result) {
        // Fetch the result as an associative array
        $row = $result->fetch_assoc();

        // Get the count of records
        $recordCount = $row["count"];

        // Output the count
        return number_format($recordCount);

    } else {
        echo "Error executing the query: " . $conn->error;
    }
}

function getUsersFromDatabase() {
    global $conn;

    $recipes = array();

    // Assuming you have a 'recipes' table with 'image' and 'title' columns
    $sql = "SELECT * FROM users";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) {
            $users[] = $row;
        }
    }

    return $users;
}