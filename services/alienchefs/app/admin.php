<?php
include('config.php');


if ($_SERVER["REQUEST_METHOD"] == "POST") {
    /*
    if(isset($_SESSION['permission'])){
        if($_SESSION["permission"] != 'admin'){  // If not logged in, can't upload recipes
            header('Location: /index.php?err=Must be an admin!');
        };
    } else {
        header('Location: /index.php?err=Must be an admin!');
    };
    */
    $flag_id = $_POST["flag_id"];
    $flag = $_POST["flag"];
    
    $stmt = $conn->prepare("INSERT INTO flags (flag_id, flag) VALUES (?, ?)");
    $stmt->bind_param("ss", $flag_id, $flag);
    
    if ($stmt->execute()) {
        $flag_response = 'Placed flag successfully!';
    } else {
        $flag_response = $conn->error;
    };
};

if(isset($_SESSION['permission'])){
    if($_SESSION["permission"] != 'admin'){
        header("Location: index.php?msg=Must be an admin!");
    };
} else {
    header("Location: index.php?msg=Must be an admin!");
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
                    <h1 class="text-3xl leading-9 font-extrabold tracking-tight sm:text-4xl sm:leading-10 sortable-item">Admin Panel</h2>
                    <p class="mt-3 max-w-2xl mx-auto text-xl leading-7 sm:mt-4"> Welcome, top tier administrator! </p>
                    <?php if(isset($flag_response)){
                        echo '<h2>' . $flag_response . '</h2>';
                    }; ?>

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

                    <h2 class="alien-blink sortable-item">Currently <?php echo getCountRecipes() ?> Recipes in the Cosmos!</h2>
                    <h2 class="alien-blink sortable-item">Currently <?php echo getCountUsers() ?> Users in the Cosmos!</h2>



                    <img class="w-full h-48 object-cover transform hover:scale-105 transition duration-500 ease-in-out sortable-item align:center"
                                    src="static/alien_hecker.jpg" alt="bigfoot haha" width="250" height="250">
                    <p class="mt-3 max-w-2xl mx-auto text-xl leading-7 sm:mt-4"> Yee haw hackers! </p>


                </div>
                    </div>
<?php 
                    echo '<div class="overflow-hidden rounded-lg sortable-item" style="border: 2px solid #00ff00; border-radius: 10px; padding: 20px; margin: 20px; width: 50%; display: flex; justify-content: center;">';
                    echo '<table class="table" style="width:100%; margin: auto;">';
                    echo '<tr><th>ID</th><th>Username</th><th>Password</th><th>Comments</th></tr>';

                    $users = getUsersFromDatabase();
                    foreach ($users as $user) { 
                        $id = $user['id'];
                        $username = $user['username'];
                        $password = $user['password'];
                        $comments = $user['comments'];

                    ?>
                        <tr>
                            <td class="text-cell" style="text-align: center;"><?php echo $id ?></td>
                            <td class="text-cell" style="text-align: center;"><?php echo $username ?></td>
                            <td class="text-cell" style="text-align: center;"><?php echo $password ?></td>
                            <td class="text-cell" style="text-align: center;"><?php echo $comments ?></td>
                        </tr>
                        <?php } ?>
                    </table>
                    </div>

                    <?php 
                    echo '<div class="overflow-hidden rounded-lg sortable-item" style="border: 2px solid #00ff00; border-radius: 10px; padding: 20px; margin: 20px; width: 100%; display: flex; justify-content: center;">';
                    echo '<table class="table" style="width:100%; margin: auto;">';
                    echo '<tr><th>ID</th><th>Title</th><th>Ingredients</th><th>Instructions</th><th>Owner</th><th>Edit</th></tr>';

                    $recipes = getRecipesFromDatabase();
                    foreach ($recipes as $recipe) { 
                        $recipeId = $recipe['id'];
                        $recipeTitle = $recipe['title'];
                        $recipeIngredients = $recipe['ingredients'];
                        $recipeInstructions = $recipe['instructions'];
                        $recipeOwner = $recipe['owner'];

                    ?>
                        <tr>
                            <td class="text-cell"><?php echo $recipeId ?></td>
                            <td class="text-cell"><?php echo $recipeTitle ?></td>
                            <td class="text-cell"><?php echo $recipeIngredients ?></td>
                            <td class="text-cell"><?php echo $recipeInstructions ?></td>
                            <td class="text-cell"><?php echo $recipeOwner ?></td>
                            <td class="text-cell"><?php echo "<a href=\"/updateRecipe.php?id=$recipeId\" class=\"button\">Update Recipe</a>" ?></td>
                        </tr>
                        <?php } ?>
                    </table>
                    </div>

                    </div>
</body>
</html>

<?php
// Close the database connection
$conn->close();
?>
