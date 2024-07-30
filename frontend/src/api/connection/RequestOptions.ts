export interface RequestOptions {
  /**
   * Body of the HTTP request as a javascript object
   * (the encoding format is handled by the connection)
   */
  body?: Record<string, any> | FormData;
  
  /**
   * Abort controller signal
   */
  signal?: AbortSignal | null;
}

/**
 * Request options that are available after being populated with defaults
 */
export interface RequestOptionsInternal {
  body?: Record<string, any> | FormData;
  signal?: AbortSignal | null;
}

/**
 * Default values for request options
 */
export const defaultRequestOptions: RequestOptionsInternal = {
  // provide values for only "mandatory" option fields
};

/**
 * Merges the user-provided options with defaults and returns the result
 */
export function populateDefaultsInRequestOptions(
  given: RequestOptions,
): RequestOptionsInternal {
  return {
    ...defaultRequestOptions,
    ...given,
  };
}
