<?php
include('connect.php');
error_reporting(0);
$email_user = $_POST['email'];
unset($_POST['email']);

$processed = 0;
foreach($_POST as $key => $value)
{
	$key = (int)$key;
	$value = (int)$value;
	$sql = "UPDATE `userratings` SET `actualrating` = $value WHERE `emailid` = '$email_user' AND `dishid` = $key";
	
	$query = mysqli_query($con, $sql);
	
	if($query == 1)
	{
		$processed += 1;
	}
}

if($processed == 15)
{
	echo 1;
}

else
{
	echo 0;
}
?>