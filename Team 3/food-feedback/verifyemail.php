<?php
include('connect.php');
error_reporting(0);
function sanitize($data)
{
	include('connect.php');
	return mysqli_real_escape_string($con, $data); // escape special characters in a string - used to prevent SQL Injection to some degree
}

if(empty($_POST) === false) // input not empty - both fields not empty
{
	$email = $_POST['email'];

	$email = sanitize($email);
	$query = mysqli_query($con, "SELECT * FROM `userratings` WHERE `emailid` = '$email'");
	$num = mysqli_num_rows($query);
	$result = ($num > 0) ? $query : 0;

	if($result === 0)
	{
		echo "user_not_found";
	}

	else
	{
		$final = array();
		while($row = mysqli_fetch_array($result))
		{
			$r = array();

			$r[] = $row['dishid'];
			$r[] = $row['dishname'];
			$r[] = $row['flavour'];
			
			$final[] = $r;
		}

		echo json_encode($final);
	}
}

?>