// Paper Trader — native macOS window for the local paper-trading control panel.
// Starts the project's Python control server (127.0.0.1 only) if it isn't already running,
// shows it in a WKWebView, and stops the server it started when the app quits.
import Cocoa
import WebKit

let port = 8765
let baseURL = URL(string: "http://127.0.0.1:\(port)/")!

// Project logs live next to the installed runtime on the external drive (installed/logs), never in ~/Library.
func logsURL() -> URL {
    URL(fileURLWithPath: projectPath()).deletingLastPathComponent().appendingPathComponent("logs")
}

func projectPath() -> String {
    if let p = Bundle.main.object(forInfoDictionaryKey: "PTProjectPath") as? String { return p }
    return "/Volumes/X10 Pro/Paper Trading Sim/installed/runtime"
}

final class AppDelegate: NSObject, NSApplicationDelegate, WKNavigationDelegate, WKUIDelegate {
    var window: NSWindow!
    var web: WKWebView!
    var server: Process?
    var splash: NSTextField!

    func applicationDidFinishLaunching(_ note: Notification) {
        buildMenu()
        let cfg = WKWebViewConfiguration()
        cfg.mediaTypesRequiringUserActionForPlayback = []
        cfg.websiteDataStore = .nonPersistent()
        web = WKWebView(frame: .zero, configuration: cfg)
        web.navigationDelegate = self
        web.uiDelegate = self
        web.setValue(false, forKey: "drawsBackground")
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1320, height: 860),
                          styleMask: [.titled, .closable, .miniaturizable, .resizable, .fullSizeContentView],
                          backing: .buffered, defer: false)
        window.title = "Paper Trader"
        window.minSize = NSSize(width: 900, height: 600)
        window.center()
        window.contentView = web
        splash = NSTextField(labelWithString: "Starting Paper Trader…")
        splash.font = NSFont.systemFont(ofSize: 15, weight: .medium)
        splash.textColor = .secondaryLabelColor
        splash.translatesAutoresizingMaskIntoConstraints = false
        web.addSubview(splash)
        NSLayoutConstraint.activate([splash.centerXAnchor.constraint(equalTo: web.centerXAnchor),
                                     splash.centerYAnchor.constraint(equalTo: web.centerYAnchor)])
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        startIfNeeded()
    }

    func ping(_ done: @escaping (Bool) -> Void) {
        var req = URLRequest(url: baseURL.appendingPathComponent("api/ping"))
        req.timeoutInterval = 1.5
        URLSession.shared.dataTask(with: req) { _, resp, _ in
            done((resp as? HTTPURLResponse)?.statusCode == 200)
        }.resume()
    }

    func startIfNeeded() {
        ping { up in
            DispatchQueue.main.async {
                if up { self.load(); return }
                let proj = projectPath()
                let py = proj + "/.venv/bin/python"
                guard FileManager.default.isExecutableFile(atPath: py) else {
                    self.fail("Can't find the project at\n\(proj)\n\nIs the external drive connected? Connect it and reopen Paper Trader.")
                    return
                }
                let p = Process()
                p.executableURL = URL(fileURLWithPath: py)
                p.arguments = [proj + "/run.py", "serve", "--port", "\(port)"]
                p.currentDirectoryURL = URL(fileURLWithPath: proj)
                let logDir = logsURL()
                guard FileManager.default.fileExists(atPath: logDir.path) else {
                    self.fail("Can't find the project log folder at\n\(logDir.path)\n\nIs the external drive connected?")
                    return
                }
                let home = URL(fileURLWithPath: proj).deletingLastPathComponent().deletingLastPathComponent().path
                var env = ProcessInfo.processInfo.environment
                env["TMPDIR"] = home + "/.cache/tmp"; env["HF_HOME"] = home + "/.cache/huggingface"
                env["TORCH_HOME"] = home + "/.cache/torch"; env["PYTHONDONTWRITEBYTECODE"] = "1"
                p.environment = env
                let logURL = logDir.appendingPathComponent("app-server.log")
                if !FileManager.default.fileExists(atPath: logURL.path) { FileManager.default.createFile(atPath: logURL.path, contents: nil) }
                if let fh = try? FileHandle(forWritingTo: logURL) { fh.seekToEndOfFile(); p.standardOutput = fh; p.standardError = fh }
                do { try p.run(); self.server = p } catch {
                    self.fail("Couldn't start the control server:\n\(error.localizedDescription)")
                    return
                }
                self.waitForServer(attempts: 60)
            }
        }
    }

    func waitForServer(attempts: Int) {
        ping { up in
            DispatchQueue.main.async {
                if up { self.load() }
                else if attempts <= 0 { self.fail("The control server didn't start. See installed/logs/app-server.log on the external drive.") }
                else { DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) { self.waitForServer(attempts: attempts - 1) } }
            }
        }
    }

    func load() {
        splash.isHidden = true
        web.load(URLRequest(url: baseURL))
    }

    func fail(_ msg: String) {
        splash.stringValue = "Paper Trader couldn't start"
        let a = NSAlert()
        a.messageText = "Paper Trader couldn't start"
        a.informativeText = msg
        a.alertStyle = .warning
        a.addButton(withTitle: "Retry")
        a.addButton(withTitle: "Quit")
        if a.runModal() == .alertFirstButtonReturn { startIfNeeded() } else { NSApp.terminate(nil) }
    }

    // Links to news sources etc. open in the default browser; the control panel stays in-app.
    func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        if let url = action.request.url, let host = url.host, host != "127.0.0.1" && host != "localhost" {
            NSWorkspace.shared.open(url)
            decisionHandler(.cancel)
            return
        }
        decisionHandler(.allow)
    }

    func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration, for action: WKNavigationAction,
                 windowFeatures: WKWindowFeatures) -> WKWebView? {
        if let url = action.request.url {
            if url.host == "127.0.0.1" || url.host == "localhost" { webView.load(URLRequest(url: url)) } else { NSWorkspace.shared.open(url) }
        }
        return nil
    }

    func webView(_ webView: WKWebView, runJavaScriptConfirmPanelWithMessage message: String, initiatedByFrame frame: WKFrameInfo,
                 completionHandler: @escaping (Bool) -> Void) {
        let a = NSAlert()
        a.messageText = message
        a.addButton(withTitle: "OK")
        a.addButton(withTitle: "Cancel")
        completionHandler(a.runModal() == .alertFirstButtonReturn)
    }

    func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String, initiatedByFrame frame: WKFrameInfo,
                 completionHandler: @escaping () -> Void) {
        let a = NSAlert()
        a.messageText = message
        a.runModal()
        completionHandler()
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) { retrySoon() }
    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) { retrySoon() }
    func retrySoon() { DispatchQueue.main.asyncAfter(deadline: .now() + 2) { self.startIfNeeded() } }

    @objc func reload(_ sender: Any?) { web.reload() }
    @objc func home(_ sender: Any?) { web.load(URLRequest(url: baseURL)) }
    @objc func back(_ sender: Any?) { web.goBack() }
    @objc func openFolder(_ sender: Any?) { NSWorkspace.shared.open(URL(fileURLWithPath: projectPath())) }
    @objc func openReports(_ sender: Any?) { NSWorkspace.shared.open(URL(fileURLWithPath: projectPath() + "/reports")) }
    @objc func openLogs(_ sender: Any?) {
        NSWorkspace.shared.open(logsURL())
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ app: NSApplication) -> Bool { true }

    func applicationWillTerminate(_ note: Notification) {
        if let s = server, s.isRunning { s.terminate() }  // only stops the server this app started
    }

    func buildMenu() {
        let main = NSMenu()
        let appItem = NSMenuItem(); main.addItem(appItem)
        let appMenu = NSMenu()
        appMenu.addItem(withTitle: "About Paper Trader", action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)), keyEquivalent: "")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Hide Paper Trader", action: #selector(NSApplication.hide(_:)), keyEquivalent: "h")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Quit Paper Trader", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        appItem.submenu = appMenu
        let editItem = NSMenuItem(); main.addItem(editItem)
        let edit = NSMenu(title: "Edit")
        edit.addItem(withTitle: "Cut", action: #selector(NSText.cut(_:)), keyEquivalent: "x")
        edit.addItem(withTitle: "Copy", action: #selector(NSText.copy(_:)), keyEquivalent: "c")
        edit.addItem(withTitle: "Paste", action: #selector(NSText.paste(_:)), keyEquivalent: "v")
        edit.addItem(withTitle: "Select All", action: #selector(NSText.selectAll(_:)), keyEquivalent: "a")
        editItem.submenu = edit
        let viewItem = NSMenuItem(); main.addItem(viewItem)
        let view = NSMenu(title: "View")
        view.addItem(withTitle: "Reload", action: #selector(reload(_:)), keyEquivalent: "r")
        view.addItem(withTitle: "Dashboard Home", action: #selector(home(_:)), keyEquivalent: "0")
        view.addItem(withTitle: "Back", action: #selector(back(_:)), keyEquivalent: "[")
        viewItem.submenu = view
        let goItem = NSMenuItem(); main.addItem(goItem)
        let go = NSMenu(title: "Files")
        go.addItem(withTitle: "Open Project Folder", action: #selector(openFolder(_:)), keyEquivalent: "")
        go.addItem(withTitle: "Open Reports Folder", action: #selector(openReports(_:)), keyEquivalent: "")
        go.addItem(withTitle: "Open Logs Folder", action: #selector(openLogs(_:)), keyEquivalent: "")
        goItem.submenu = go
        let winItem = NSMenuItem(); main.addItem(winItem)
        let win = NSMenu(title: "Window")
        win.addItem(withTitle: "Minimize", action: #selector(NSWindow.performMiniaturize(_:)), keyEquivalent: "m")
        win.addItem(withTitle: "Close", action: #selector(NSWindow.performClose(_:)), keyEquivalent: "w")
        winItem.submenu = win
        NSApp.mainMenu = main
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.regular)
app.run()
