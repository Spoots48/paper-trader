// Draws the app icon (1024x1024 PNG): a green rounded square with a rising chart line.
import Cocoa

let size = 1024.0
let img = NSImage(size: NSSize(width: size, height: size))
img.lockFocus()
let inset = 100.0
let rect = NSRect(x: inset, y: inset, width: size - 2 * inset, height: size - 2 * inset)
let path = NSBezierPath(roundedRect: rect, xRadius: 185, yRadius: 185)
NSGradient(starting: NSColor(calibratedRed: 0.20, green: 0.52, blue: 0.38, alpha: 1),
           ending: NSColor(calibratedRed: 0.10, green: 0.30, blue: 0.23, alpha: 1))!.draw(in: path, angle: -90)
// faint grid
NSColor(white: 1, alpha: 0.10).setStroke()
for i in 1...3 {
    let y = inset + Double(i) * (size - 2 * inset) / 4
    let g = NSBezierPath(); g.move(to: NSPoint(x: inset + 90, y: y)); g.line(to: NSPoint(x: size - inset - 90, y: y))
    g.lineWidth = 6; g.stroke()
}
// chart line
let pts: [(Double, Double)] = [(0.20, 0.33), (0.38, 0.47), (0.52, 0.40), (0.68, 0.58), (0.80, 0.70)]
let line = NSBezierPath()
for (i, p) in pts.enumerated() {
    let pt = NSPoint(x: p.0 * size, y: p.1 * size)
    if i == 0 { line.move(to: pt) } else { line.line(to: pt) }
}
line.lineWidth = 58; line.lineCapStyle = .round; line.lineJoinStyle = .round
NSColor.white.setStroke(); line.stroke()
// arrow head
let tip = NSPoint(x: 0.80 * size, y: 0.70 * size)
let head = NSBezierPath()
head.move(to: NSPoint(x: tip.x - 150, y: tip.y + 12)); head.line(to: NSPoint(x: tip.x + 18, y: tip.y + 18)); head.line(to: NSPoint(x: tip.x + 12, y: tip.y - 150))
head.lineWidth = 58; head.lineCapStyle = .round; head.lineJoinStyle = .round; head.stroke()
img.unlockFocus()
let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
let png = rep.representation(using: .png, properties: [:])!
try! png.write(to: URL(fileURLWithPath: CommandLine.arguments[1]))
