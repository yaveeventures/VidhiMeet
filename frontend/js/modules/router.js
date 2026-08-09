/**
 * VidhiMeet Client-Side PushState Router
 * Provides clean URL routing, browser history back/forward handling, and deep linking.
 */

export class ClientRouter {
  constructor(routes = {}) {
    self.routes = routes;
    window.addEventListener('popstate', (e) => this.handlePopState(e));
  }

  register(path, handler) {
    this.routes[path] = handler;
  }

  navigate(path, state = {}) {
    window.history.pushState(state, '', path);
    this.resolve(path, state);
  }

  resolve(path = window.location.pathname, state = {}) {
    const routeHandler = this.routes[path] || this.routes['*'];
    if (typeof routeHandler === 'function') {
      routeHandler(path, state);
    }
  }

  handlePopState(event) {
    this.resolve(window.location.pathname, event.state || {});
  }
}

export const router = new ClientRouter();
