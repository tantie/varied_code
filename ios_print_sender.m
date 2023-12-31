-(IBAction)printbtnpress:(id)sender {
    NSLog(@"Printing...");
    NSData *imageData = UIImagePNGRepresentation(_saveimage);

    // Настройка конфигурации сессии с заданным временем ожидания
    NSURLSessionConfiguration *configuration = [NSURLSessionConfiguration defaultSessionConfiguration];
    configuration.timeoutIntervalForRequest = 5.0; // 10 секунд на запрос
    configuration.timeoutIntervalForResource = 180.0; // 180 секунд на загрузку ресурса

    // Создание сессии с этой конфигурацией
    NSURLSession *session = [NSURLSession sessionWithConfiguration:configuration];

    // Создание и настройка запроса
    NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:[NSURL URLWithString:@"http://****:5000/print/"]];
    [request setHTTPMethod:@"POST"];
    [request setHTTPBody:imageData];

    // Задача для выполнения запроса
    NSURLSessionDataTask *task = [session dataTaskWithRequest:request completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
        // Выполнение кода в главном потоке, так как мы обновляем UI
        dispatch_async(dispatch_get_main_queue(), ^{
            if (error) {
                NSLog(@"Error: %@", error);
                // Показываем сообщение об ошибке, если есть
                UIAlertController *alertController = [UIAlertController alertControllerWithTitle:@"Error" message:@"Printer unavailable. Pleace check it" preferredStyle:UIAlertControllerStyleAlert];
                UIAlertAction *okAction = [UIAlertAction actionWithTitle:@"OK" style:UIAlertActionStyleDefault handler:nil];
                [alertController addAction:okAction];
                [self presentViewController:alertController animated:YES completion:nil];
            } else {
                // Обработка полученных данных
                NSString *responseString = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
                NSLog(@"Response: %@", responseString);
                
                // Отображаем ответ сервера
                UIAlertController *alertController = [UIAlertController alertControllerWithTitle:@"Success" message:responseString preferredStyle:UIAlertControllerStyleAlert];
                UIAlertAction *okAction = [UIAlertAction actionWithTitle:@"OK" style:UIAlertActionStyleDefault handler:nil];
                [alertController addAction:okAction];
                [self presentViewController:alertController animated:YES completion:nil];
            }
        });
    }];

    // Запуск задачи
    [task resume];
}
