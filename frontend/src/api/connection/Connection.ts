import {
  RequestOptions,
  populateDefaultsInRequestOptions,
} from "./RequestOptions";

/**
 * Represents an HTTP-level connection to the backend API
 */
export class Connection {
  // NOTE: state can be stored here, such as the authentication token

  constructor() {
    // nothing needed currently
  }

  /**
   * Makes an HTTP request to a given URL
   */
  public async request(
    method: string,
    relativeUrl: string,
    options?: RequestOptions,
  ): Promise<Response> {
    const _options = populateDefaultsInRequestOptions(options || {});

    // specify request headers
    let headers = {
      Accept: "application/json",
    };

    // prepare request body
    let body: any = undefined;
    if (_options.body !== undefined) {
      if (_options.body instanceof FormData) {
        // keep FormData as is, Content-Type is added by fetch
        body = _options.body;
      } else {
        // encode as JSON by default
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(_options.body);
      }
    }

    // prepare request options
    let requestInit: RequestInit = {
      method,
      headers,
      body,
    };

    // send the request
    return await fetch(this.url(relativeUrl), requestInit);
  }

  /**
   * Constructs full URL from only a relative portion of it
   */
  public url(relativeUrl: string): URL {
    return new URL(
      relativeUrl,
      "http://localhost:1817/", // TODO: get from config
    );
  }
}
