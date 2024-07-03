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
    const headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
    };

    // send the request
    return await fetch(this.url(relativeUrl), {
      method,
      headers,
      body: _options.body ? JSON.stringify(_options.body) : undefined,
    });
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