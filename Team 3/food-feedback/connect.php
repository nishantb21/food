<?php
// establish connection with the databse 
$connect_error = "Sorry, Unable to connect to the database";

$con = mysqli_connect('localhost', 'root', '', 'foodback');

// throw an error if the connection fails
if (!$con) {
    die('Connect Error: ' . mysqli_connect_errno() . $connect_error);
}
?>