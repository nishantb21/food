<?php
include('connect.php');

$sql = "SELECT * FROM `userratings`";

$query = mysqli_query($con, $sql);

print_r($query);
?>