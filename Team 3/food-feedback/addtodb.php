<?php
include('connect.php');
error_reporting(0);
$email_user = $_POST['email'];
unset($_POST['email']);

$processed = 0;
foreach($_POST as $key => $value)
{
	$arr = explode("-", $key);

	$key = (int)$arr[1];
	$value = (int)$value;
	if($arr[0] == "dish")
	{
		$sql = "UPDATE `userratings` SET `actualrating` = $value WHERE `emailid` = '$email_user' AND `dishid` = $key";
	}
	elseif ($arr[0] == "flavour") 
	{
		$sql = "UPDATE `userratings` SET `actualflavour` = $value WHERE `emailid` = '$email_user' AND `dishid` = $key";
	}

	$query = mysqli_query($con, $sql);
	
	if($query == 1)
	{
		$processed += 1;
	}
}

if($processed == 30)
{
	echo "<script>alert('Your response has been recorded, Thank you for helping out, you can now close the tab');
		window.location.href='index.html';
		</script>";
}

else
{
	echo "<script>alert('There was an error trying to record your response, please try again');
		window.location.href='index.html';
		</script>";
}
?>