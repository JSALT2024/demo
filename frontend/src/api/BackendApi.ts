import { Connection } from "./connection/Connection";
import { VideosApi } from "./VideosApi";

export class BackendApi {

  /**
   * HTTP-level connection object
   */
  public readonly connection: Connection;

  public videos: VideosApi;

  private constructor() {
    this.connection = new Connection();

    this.videos = new VideosApi(this.connection);
  }

  //////////////////////////////
  // API Instance Persistence //
  //////////////////////////////

  private static CURRENT_API_INSTANCE: BackendApi | null = null;

  /**
   * Returns the current API connection that should be used by the app
   */
  public static current() {
    if (this.CURRENT_API_INSTANCE === null) {
      // here, the API connection default instance is created
      this.CURRENT_API_INSTANCE = new BackendApi();
    }

    return this.CURRENT_API_INSTANCE;
  }

}