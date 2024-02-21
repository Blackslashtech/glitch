<?php
include('config.php');

if(isset($_SESSION['permission'])){
    if($_SESSION["permission"] != 'admin'){
        header("Location: index.php?msg=Must be an admin!");
    };
} else {
    header("Location: index.php?msg=Must be an admin!");
};

if($_SERVER["REQUEST_METHOD"] == "POST"){
    $title = $_POST["title"];
    $ingredients = $_POST["ingredients"];
    $instructions = $_POST["instructions"];
    $owner = $_POST['owner'];
    $id = $_POST['id'];
    
    // Check if file was uploaded without errors
    if(isset($_FILES["image"]) && $_FILES["image"]["error"] == 0){
        $image = file_get_contents($_FILES["image"]["tmp_name"]);
        $image = bin2hex($image);
        $stmt = $conn->prepare("UPDATE recipes set title=?, ingredients=?, instructions=?, owner=?, image=? WHERE id=?");
        $null = NULL;
        $stmt->bind_param("ssssbi", $title, $ingredients, $instructions, $owner, $null, $id);
        $stmt->send_long_data(3, $image);
    } else {    
        $stmt = $conn->prepare("UPDATE recipes set title=?, ingredients=?, instructions=?, owner=? WHERE id=?");
        $null = NULL;
        $stmt->bind_param("ssssi", $title, $ingredients, $instructions, $owner, $id);
    };
    
    if ($stmt->execute()) {
        // echo '<div class="alien-error">New record created successfull!</div>';
        header("Location: updateRecipe.php?id=" . $_POST['id']);
    } else {
        echo '<div class="alien-error">Error: ' . $sql . "</div>" . $conn->error;
    };
};
// Allow admins to view all users
// Allow admins to review all recipes
?>

<!DOCTYPE html>
<html class='w-full h-full overflow-hidden hide-scrollbar' style="background: #000 url('alien-bg.jpg') no-repeat center center fixed; -webkit-background-size: cover; -moz-background-size: cover; -o-background-size: cover; background-size: cover;">
    
<head>
    <!-- Include your stylesheets and other head elements here -->
    <link rel="stylesheet" type="text/css" href="alien.css">
</head>

<body class='relative h-screen w-screen flex items-center flex-col' style="font-family: 'Orbitron', sans-serif; color: #00ff00;">
<div id="aliens-layer"></div>
    <script src="static/aliens.js"></script>
    <!-- ... (previous HTML code) ... -->
                <div class="text-center mb-12 sortable-item">
                    <h1 class="text-3xl leading-9 font-extrabold tracking-tight sm:text-4xl sm:leading-10 sortable-item">Update Recipe!</h2>
                    <p class="mt-3 max-w-2xl mx-auto text-xl leading-7 sm:mt-4"> Welcome, top tier administrator! </p>

                    <p><a href="/index.php" class="button">Go to Home Page</a>
                    <?php 
                    if(isset($_SESSION['loggedin'])){
                        if($_SESSION['loggedin'] == true){
                            echo '<a href="/logout.php" class="button">Logout</a>';
                        };} 
                    else {
                        echo '<a href="/login.php" class="button">Login</a>';
                        };
                    ?>
                    <a href="/allrecipes.php" class="button">All Recipes</a><a href="/upload.php" class="button">Upload Recipe</a>
                    <?php 
                    if(isset($_SESSION['permission'])){
                        if($_SESSION['permission'] == 'admin'){
                            echo '<a href="/admin.php" class="button">Admin Panel</a>';
                        };
                    };
                    ?>
                    </p>
                    <?php 
                    if(isset($_SESSION['loggedin'])){
                        if($_SESSION['loggedin'] == true){
                            echo '<h4 class="sortable-item">Hello ' . $_SESSION['username'] . '! You have permission level ' . $_SESSION['permission'] . '</h2>';
                        } else {
                            echo '<h4 class="sortable-item">Not logged in :(</h2>';
                        };
                    };
                    ?>

<?php if(isset($_GET['err'])){
    echo '<div class="alien-error">' . $_GET['err'] . '</div>';
};

if(isset($_GET['id'])){
    $recipes = getSingleRecipe($_GET['id']);
    foreach ($recipes as $recipe){
        ?>
                    
                    
                    <form action="updateRecipe.php" method="post" enctype="multipart/form-data">
                        <label for="title">ID:</label><br>
                        <input type="text" id="id" name="id" readonly value="<?php echo $recipe['id'] ?>"><br>
                        <label for="title">Title:</label><br>
                        <input type="text" id="title" name="title" value="<?php echo $recipe['title'] ?>"><br>
                        <label for="ingredients">Ingredients:</label><br>
                        <textarea id="ingredients" name="ingredients" rows="4" type="text" cols="50"><?php echo $recipe['ingredients'] ?></textarea><br>
                        <label for="instructions">Instructions:</label><br>
                        <textarea id="instructions" name="instructions" rows="4" type="text" cols="50"><?php echo $recipe['instructions'] ?></textarea><br>
                        <label for="owner">Owner:</label><br>
                        <textarea id="owner" name="owner" rows="1" type="text" cols="50"><?php echo $recipe['owner'] ?></textarea><br>
                        <label for="image">Select image:</label>
                        <input type="file" class="button" id="image" name="image">
                        <input type="submit" class="button" value="Update Recipe">
                        <br><br>
                        <img class="w-full h-48 object-cover transform hover:scale-105 transition duration-500 ease-in-out sortable-item" src="<?php echo 'getimg.php?id=' . $recipe['id'] ?>"
                    </form> 
                    <?php
                    }
                } else {
                    echo '<div class="alien-error">Must have a recipe ID set!</div>';
                };
                ?>
                </div>
                
            </div>
            </div>
</body>
</html>

<?php
// Close the database connection
$conn->close();
?>
