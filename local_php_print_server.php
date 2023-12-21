<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $imagePath = "/home/pi/www/html/1.jpg"; // Укажите полный путь к изображению
    $printerName = "printer"; // Имя вашего принтера

    // Создаем новое изображение с белыми полями
    $imagick = new Imagick($imagePath);

    $originalWidth = $imagick->getImageWidth();
    $originalHeight = $imagick->getImageHeight();

    $newWidth = $originalWidth * 1.114; // увеличиваем ширину на 11.4% для компенсации размеров

    $x = ($newWidth - $originalWidth) / 2;

    $imagick->borderImage('white', $x, 0);

    $tempImagePath = "/tmp/temp_print_image.jpg";
    $imagick->writeImage($tempImagePath);
    $imagick->clear();
    $imagick->destroy();

    // Команда для отправки на печать
    $command = "lp -d " . escapeshellarg($printerName) . " " . escapeshellarg($tempImagePath);
   
    // Выполнение команды и захват результата
    $output = shell_exec($command . " 2>&1");

    // Вывод результата
    echo "Command: " . htmlspecialchars($command) . "<br>";
    echo "Output: <pre>" . htmlspecialchars($output) . "</pre>";

if (preg_match('/printer-(\d+)/', $output, $matches)) {
    $jobId = (int) $matches[1]; // преобразовываем строку в число
    echo "Job ID: " . $jobId;
} else {
    echo "Job ID not found in output.";
}
    echo "Image attempted to send to printer!";
    exit();
}
?>
