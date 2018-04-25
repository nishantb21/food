<?php
session_start();
include('connect.php');
$email_user = $_SESSION['emailid'];

// $sql = "SELECT * FROM `userflavours` WHERE `emailid` = '$email_user'";
// $query = mysqli_query($con, $sql);

// $final = array();

// while($row = mysqli_fetch_array($query))
// {
// 	$r = array();

// 	$r[] = $row['dishid'];
// 	$r[] = $row['dishname'];
// 	$r[] = $row['flavour'];

// 	$final[] = $r;
// }

// echo json_encode($final);
?>