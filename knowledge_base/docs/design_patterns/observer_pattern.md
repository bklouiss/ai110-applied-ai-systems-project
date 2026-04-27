# Observer Pattern

## Overview

The Observer pattern defines a one-to-many dependency between objects. When one object (the **Subject**) changes state, all registered dependents (**Observers**) are notified and updated automatically. It is a behavioral design pattern that promotes loose coupling: the Subject knows observers exist, but not what they do with the notification.

---

## Structure

- **Subject (Observable):** Holds a list of Observer references. Provides `subscribe`, `unsubscribe`, and `notify` methods. Calls `notify` whenever its state changes.
- **Observer (interface/ABC):** Declares a single `update(event, data)` method that all concrete observers must implement.
- **Concrete Observers:** Implement `update()` in their own way — one might log, another refresh a UI, another trigger an alert.

---

## When to Use

- Multiple parts of a system must react to the same event, but you want them decoupled from the source.
- The number of dependents is unknown at design time or changes at runtime (subscribe/unsubscribe dynamically).
- A change in one object requires updating others, but you don't know how many or what kind.

---

## When Not to Use

- Only one consumer — a direct function call or callback is clearer and cheaper.
- Notification order matters and must be guaranteed — Observer provides no ordering contract.
- You need the return value of the notification — use Command or a direct call instead.
- Observers are long-running or synchronous and you need non-blocking behavior — use an async event bus instead.

---

## Real-World Examples

- **UI frameworks:** A data model notifies a chart, a table, and a status bar whenever state changes.
- **DOM events:** A single click event notifies multiple registered listeners independently.
- **Reactive programming:** RxPY / RxJS observables formalize this pattern with composable operators.
- **This project:** When a new document is indexed into ChromaDB, the embedding pipeline, the collection metadata, and any UI search index all need to update.

---

## Related Patterns

| Pattern | Relationship |
|---------|-------------|
| Mediator | Centralizes all inter-object communication; Observer broadcasts from one source |
| Event Bus | Decoupled Observer — subjects and observers don't hold direct references to each other |
| Publish-Subscribe | Like Observer but routed through a message broker; full decoupling between publisher and subscriber |
| Command | Use instead of Observer when you need the result of the notification or need to queue/undo it |
