/*
This is a simple code that turns your iPhone into a proxy server if your provider restricts access to the hotspot.

Connect to you iphone and configure your computer's browser to use your iPhone as a proxy server (specify your iPhone's IP address and port 8080).
The IP address is usually 172.20.10.1, or "your iPhone name".local.

 "File" > "Swift Packages" > "Add Package Dependency"
 https://github.com/httpswift/swifter.git
*/

import SwiftUI
import UIKit
import Swifter

@main
struct Hotspot_ProxyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> ViewController {
        return ViewController()
    }

    func updateUIViewController(_ uiViewController: ViewController, context: Context) {}
}

class ViewController: UIViewController {
    
    var server: HttpServer?
    var statusLabel: UILabel!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .white
        
        statusLabel = UILabel()
        statusLabel.text = "Server is stopped"
        statusLabel.textAlignment = .center
        statusLabel.translatesAutoresizingMaskIntoConstraints = false
        
        let startButton = UIButton(type: .system)
        startButton.setTitle("Start Server", for: .normal)
        startButton.addTarget(self, action: #selector(startServer), for: .touchUpInside)
        startButton.translatesAutoresizingMaskIntoConstraints = false
        startButton.backgroundColor = .systemGreen
        startButton.setTitleColor(.white, for: .normal)
        startButton.layer.cornerRadius = 10
        
        let stopButton = UIButton(type: .system)
        stopButton.setTitle("Stop Server", for: .normal)
        stopButton.addTarget(self, action: #selector(stopServer), for: .touchUpInside)
        stopButton.translatesAutoresizingMaskIntoConstraints = false
        stopButton.backgroundColor = .systemRed
        stopButton.setTitleColor(.white, for: .normal)
        stopButton.layer.cornerRadius = 10
        
        let stackView = UIStackView(arrangedSubviews: [statusLabel, startButton, stopButton])
        stackView.axis = .vertical
        stackView.spacing = 20
        stackView.translatesAutoresizingMaskIntoConstraints = false
        
        view.addSubview(stackView)
        
        NSLayoutConstraint.activate([
            stackView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            stackView.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            startButton.widthAnchor.constraint(equalToConstant: 200),
            stopButton.widthAnchor.constraint(equalToConstant: 200),
        ])
    }
    
    @objc func startServer() {
        server = HttpServer()
        
        server?["/.*"] = { request in
            self.proxyRequest(request)
        }
        
        do {
            try server?.start(8080)
            updateStatusLabel(isRunning: true)
            print("Server has started (port = 8080). Try to connect now...")
        } catch {
            print("Server start error: \(error)")
        }
    }
    
    func proxyRequest(_ request: HttpRequest) -> HttpResponse {
        guard let url = URL(string: request.path.dropFirst().description) else {
            return .badRequest(nil)
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = request.method.uppercased()
        
        for (headerField, headerValue) in request.headers {
            urlRequest.setValue(headerValue, forHTTPHeaderField: headerField)
        }
        
        urlRequest.httpBody = Data(request.body)
        
        let semaphore = DispatchSemaphore(value: 0)
        var responseData: Data?
        var responseError: Error?
        var responseCode: Int = 500
        
        let task = URLSession.shared.dataTask(with: urlRequest) { data, response, error in
            responseData = data
            responseError = error
            responseCode = (response as? HTTPURLResponse)?.statusCode ?? 500
            semaphore.signal()
        }
        
        task.resume()
        semaphore.wait()
        
        if let error = responseError {
            print("Proxy request error: \(error)")
            return .internalServerError
        }
        
        return .raw(responseCode, "OK", nil) { writer in
            if let data = responseData {
                try? writer.write(data)
            }
        }
    }
    
    @objc func stopServer() {
        server?.stop()
        server = nil
        updateStatusLabel(isRunning: false)
        print("Server has stopped.")
    }
    
    func updateStatusLabel(isRunning: Bool) {
        if isRunning {
            statusLabel.text = "Server is running"
            statusLabel.textColor = .systemGreen
        } else {
            statusLabel.text = "Server is stopped"
            statusLabel.textColor = .systemRed
        }
    }
}
