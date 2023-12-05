<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>菜鸟教程(runoob.com) urllib POST  测试</title>
</head>
<body>
<form action="" method="post" name="myForm">
    Name: <input type="text" name="name"><br>
    Tag: <input type="text" name="tag"><br>
    <input type="submit" value="提交">
</form>
<hr>
<?php
// 使用 PHP 来获取表单提交的数据，你可以换成其他的
if(isset($_POST['name']) && $_POST['tag'] ) {
   echo $_POST["name"] . ', ' . $_POST['tag'];
}
?>
</body>
</html>