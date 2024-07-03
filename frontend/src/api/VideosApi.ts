import { Connection } from "./connection/Connection";
import { Video } from "./model/Video";

export class VideosApi {
  private connection: Connection;

  constructor(connection: Connection) {
    this.connection = connection;
  }

  async list(): Promise<Video[]> {
    const response = await this.connection.request("GET", "videos");
    if (response.status !== 200) {
      throw response;
    }
    return (await response.json()) as Video[];
  }

  async upload(videoBlob: Blob, videoTitle: string): Promise<void> {
    const body = new FormData();
    body.append(
      "file", // parameter name
      videoBlob, // video binary data
      videoTitle, // file name
    );

    const response = await this.connection.request("POST", "videos", { body });
    
    if (response.status !== 201) {
      throw response;
    }
  }
}