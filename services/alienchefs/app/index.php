<?php
include('config.php');
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
                <?php 
                    if(isset($_GET['msg'])){
                        echo '<div class="alien-error">' . $_GET['msg'] . '</div>';
                    };
                ?>
                    <h1 class="text-3xl leading-9 font-extrabold tracking-tight sm:text-4xl sm:leading-10 sortable-item">Intergalactic Cuisine: Where Flavor Meets the Cosmos</h2>
                    <p class="mt-3 max-w-2xl mx-auto text-xl leading-7 sm:mt-4"> Welcome, brave gastronauts, to a culinary journey that defies gravity, embraces the unknown, and tickles your taste buds with flavors from the far reaches of the cosmos! Step aboard our spaceship of flavors as we embark on a gastronomic adventure like no other. </p>
                    <p>At Intergalactic Cuisine, we're not just about earthly recipes. We've made contact with extraterrestrial master chefs from distant planets, mysterious moons, and hidden asteroid foodie havens. These cosmic culinary pioneers have opened their kitchens to share their closely guarded secrets and tantalizing recipes with us mere Earthlings.</p>

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
                            echo '<h4 class="sortable-item">Hello ' . $_SESSION['username'] . '! You have permission level ' . $_SESSION['permission'] . '. Your comments are ' . $_SESSION['comments'] . '</h2>';
                        } else {
                            echo '<h4 class="sortable-item">Not logged in :(</h2>';
                        };
                    };
                    ?>

                    <h2 class="alien-blink sortable-item">Currently <?php echo getCountRecipes() ?> Recipes in the Cosmos!</h2>


                    <h2 class="text-3xl leading-9 font-extrabold tracking-tight sm:text-4xl sm:leading-10 sortable-item">Cooking with Cryptids</h2>
                    <img class="w-full h-48 object-cover transform hover:scale-105 transition duration-500 ease-in-out sortable-item"
                                    src="static/cookin_with_cryptids.jpg" alt="bigfoot haha" width="500" height="500">
                    <p class="mt-3 max-w-2xl mx-auto text-xl leading-7 sm:mt-4"> Ever wondered what the Chupacabra's favorite midnight snack is? Or how the elusive Sasquatch likes to season its forest foraged finds? Our collection of cryptid-inspired recipes will unveil the culinary wonders of these elusive creatures. You might even catch a glimpse of Bigfoot's secret spice stash or discover why the Loch Ness Monster has been hiding its culinary prowess for centuries. </p>

                    <h2 class="text-3xl leading-9 font-extrabold tracking-tight sm:text-4xl sm:leading-10 sortable-item">Taste the Unknown</h2>
                    <p class="mt-3 max-w-2xl mx-auto text-xl leading-7 sm:mt-4"> Prepare your taste buds for a warp-speed ride through taste and texture. Our recipes will introduce you to ingredients that defy gravity, dishes that change colors at will, and desserts that teleport onto your plate. It's not just a meal; it's a dining experience that will leave you questioning reality.</p>
                    <p class="mt-3 max-w-2xl mx-auto text-xl leading-7 sm:mt-4">So, fellow culinary explorers, fasten your seatbelts, adjust your space goggles, and prepare for a journey through uncharted flavors. From the delightful to the downright bizarre, Intergalactic Cuisine has it all. Join us as we boldly go where no taste bud has gone before!</p>



                </div>
                <?php

                if(isset($_GET['rand'])){
                    $recipes = getRandomRecipes($_GET['rand']);
                    echo '<h1 class="sortable-item" style="align:center">' . $_GET['rand'] .' random recipies!</h1>';

                } else {
                    $recipes = getRandomRecipes(5);
                    echo '<h1 class="sortable-item" style="align:center"> Five random recipies!</h1>';
                }

                    foreach ($recipes as $recipe) {
                        // $recipeImage = $recipe['image'];
                        $recipeIngredients = $recipe['ingredients'];
                        $recipeTitle = $recipe['title'];
                        $recipeId = $recipe['id'];
                        $recipeInstructions = $recipe['instructions'];
                        $recipeOwner = $recipe['owner'];

                        // // Resize image
                        // list($width, $height) = getimagesize($recipeImage);
                        // $newWidth = 500;
                        // $newHeight = 500;

                        // $thumb = imagecreatetruecolor($newWidth, $newHeight);
                        // $source = imagecreatefromjpeg($recipeImage);

                        // imagecopyresampled($thumb, $source, 0, 0, 0, 0, $newWidth, $newHeight, $width, $height);
                        // imagejpeg($thumb, $recipeImage, 100);
                        ?>
                        <div class="overflow-hidden rounded-lg sortable-item" style="border: 2px solid #00ff00; border-radius: 10px; padding: 20px; margin: 20px;">
                        <table class="table">
                            <tr>
                                <th colspan="3" class="text-lg font-semibold sortable-item">
                                    <h2><?php echo $recipeTitle; ?></h3>
                                    <p><?php echo $recipeOwner ?></p>
                            </tr>
                            <tr>
                                <td rowspan="3">
                                    <img class="w-full h-48 object-cover transform hover:scale-105 transition duration-500 ease-in-out sortable-item"
                                    src="<?php echo 'getimg.php?id=' . $recipeId ?>" alt="<?php echo $recipeTitle; ?>" width="500" height="500">
                                </td>
                            </tr>
                            <tr>
                                <td class="text-cell"><b>Ingredients</b><p><?php echo $recipeIngredients ?></td>
                                <td class="text-cell"><b>Instructions</b><p><?php echo $recipeInstructions ?></td>
                            </tr>
                        </table>
                        </div>
                    <?php } ?>


    <!-- ... (rest of the HTML code) ... -->
    <div class="text-center mb-12 sortable-item">
                    <h2 class="text-3xl leading-9 font-extrabold tracking-tight sm:text-4xl sm:leading-10 sortable-item">Uploads</h2>
                    <p class="mt-3 max-w-2xl mx-auto text-xl leading-7 sm:mt-4">Have a zany recipe to share? Upload it here to share it!</p>
                    <p><a href="/upload.php" class="button">Go to Upload Page</a></p>
    </div>
                    <!-- <script src="static/aliens.js"></script> -->
                    </div>
</body>
</html>

<?php
// Close the database connection
$conn->close();
?>
