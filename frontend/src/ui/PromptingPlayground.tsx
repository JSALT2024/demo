import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  FormControl,
  FormLabel,
  Stack,
  Switch,
  Textarea,
  Typography,
} from "@mui/joy";
import { useClipState } from "./useClipState";
import { ClipsCollection } from "../api/model/ClipsCollection";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import TheatersIcon from "@mui/icons-material/Theaters";
import ChatIcon from "@mui/icons-material/Chat";
import { BackendApi } from "../api/BackendApi";

// Taken from:
// https://github.com/JSALT2024/Sign_LLaVA/blob/multi_task/llava/constants.py
const PROMPT_OPTIONS = {
  translate_with_context:
    "Here are some preceding sentences as context: '<context>'. Translate " +
    "the next sentence given by the American Sign Language video into English. ",
  translate_no_context:
    "Translate the given American Sign Language video into English. ",
  one_word_present:
    "Given the ASL video input, answer the following question with 'yes' or " +
    "'no': Is the sign '<word>' present? ",
  multi_words_present:
    "Given the ASL video input, answer the following questions with 'yes' " +
    "or 'no' for each sign listed, separated by commas: Are the signs " +
    "'<words>' present?",
  is_reversed:
    "Given the video input, answer the following question with 'yes' or " +
    "'no': Is the video presented in reversed temporal order?",
};

export interface PromptingPlaygroundProps {
  readonly videoId: string;
  readonly clipIndex: number;
  readonly clipsCollection: ClipsCollection;
}

export function PromptingPlayground(props: PromptingPlaygroundProps) {
  const clipIndex = props.clipIndex;
  const clipsCollection = props.clipsCollection;
  const clip = clipsCollection.clips[clipIndex];

  const [useMaeEmbeddings, setUseMaeEmbeddings] = useClipState<boolean>(
    clipIndex,
    true,
  );
  const [useDinoEmbeddings, setUseDinoEmbeddings] = useClipState<boolean>(
    clipIndex,
    true,
  );
  const [useS2vEmbeddings, setUseS2vEmbeddings] = useClipState<boolean>(
    clipIndex,
    true,
  );

  const [isLoading, setIsLoading] = useClipState<boolean>(clipIndex, false);
  const [customPrompt, setCustomPrompt] = useClipState<string>(clipIndex, "");
  const [llmResponse, setLlmResponse] = useClipState<string>(clipIndex, "");

  function setTranslationPrompt() {
    if (clip.translation_context === null) {
      setCustomPrompt(PROMPT_OPTIONS.translate_no_context);
      return;
    }

    setCustomPrompt(
      PROMPT_OPTIONS.translate_with_context.replace(
        "<context>",
        clip.translation_context,
      ),
    );
  }

  async function sendCustomPrompt() {
    const api = BackendApi.current();

    setIsLoading(true);
    const response = await api.videos.retranslate(
      props.videoId,
      clip.clip_index,
      {
        use_mae: useMaeEmbeddings,
        use_dino: useDinoEmbeddings,
        use_sign2vec: useS2vEmbeddings,
        prompt: customPrompt,
      },
    );
    setLlmResponse(response);
    setIsLoading(false);
  }

  return (
    <Box sx={{ paddingTop: 5 }}>
      <Typography
        level="h2"
        sx={{ marginBottom: 2 }}
        startDecorator={<ChatIcon />}
        endDecorator={
          <Chip variant="soft" startDecorator={<TheatersIcon />}>
            Clip index {clipIndex} of {clipsCollection.clips.length}
          </Chip>
        }
      >
        Prompting playground
      </Typography>

      {/* Visual embeddings toggles */}
      <Stack direction="column" spacing={1} sx={{ maxWidth: "300px" }}>
        <FormControl
          orientation="horizontal"
          sx={{ justifyContent: "space-between" }}
        >
          <FormLabel>Use visual MAE embeddings</FormLabel>
          <Switch
            checked={useMaeEmbeddings}
            onChange={(e) => setUseMaeEmbeddings(e.target.checked)}
            color={useMaeEmbeddings ? "primary" : "neutral"}
          />
        </FormControl>
        <FormControl
          orientation="horizontal"
          sx={{ justifyContent: "space-between" }}
        >
          <FormLabel>Use visual DINO embeddings</FormLabel>
          <Switch
            checked={useDinoEmbeddings}
            onChange={(e) => setUseDinoEmbeddings(e.target.checked)}
            color={useDinoEmbeddings ? "primary" : "neutral"}
          />
        </FormControl>
        <FormControl
          orientation="horizontal"
          sx={{ justifyContent: "space-between" }}
        >
          <FormLabel>Use visual Sign2Vec embeddings</FormLabel>
          <Switch
            checked={useS2vEmbeddings}
            onChange={(e) => setUseS2vEmbeddings(e.target.checked)}
            color={useS2vEmbeddings ? "primary" : "neutral"}
          />
        </FormControl>
      </Stack>

      <Typography level="h3" sx={{ marginTop: 2 }} gutterBottom>
        User prompt
      </Typography>
      <Stack direction="row" spacing={1} sx={{ marginTop: 2 }}>
        <Button variant="soft" size="sm" onClick={setTranslationPrompt}>
          Translation
        </Button>
        <Button
          variant="soft"
          size="sm"
          onClick={(e) => setCustomPrompt(PROMPT_OPTIONS.one_word_present)}
        >
          1 Keyword
        </Button>
        <Button
          variant="soft"
          size="sm"
          onClick={(e) => setCustomPrompt(PROMPT_OPTIONS.multi_words_present)}
        >
          N Keywords
        </Button>
        <Button
          variant="soft"
          size="sm"
          onClick={(e) => setCustomPrompt(PROMPT_OPTIONS.is_reversed)}
        >
          Is Reversed
        </Button>
        <Button
          variant="soft"
          size="sm"
          disabled={customPrompt === ""}
          onClick={(e) => setCustomPrompt("")}
        >
          Custom
        </Button>
      </Stack>
      <Stack direction="row" spacing={1} sx={{ marginTop: 2 }}>
        <Textarea
          placeholder="Your custom prompt..."
          variant="outlined"
          sx={{ flexGrow: 1 }}
          value={customPrompt}
          onChange={(e) => setCustomPrompt(e.target.value)}
          disabled={isLoading}
        />
        <Button onClick={sendCustomPrompt} disabled={isLoading}>
          Send
        </Button>
      </Stack>
      {isLoading && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            marginTop: 3,
          }}
        >
          <CircularProgress variant="soft" />
        </Box>
      )}
      {llmResponse && (
        <>
          <Typography level="h4" sx={{ marginTop: 2 }} gutterBottom>
            Sign LLaVA response
          </Typography>
          <Alert color="neutral" startDecorator={<SmartToyIcon />}>
            {llmResponse}
          </Alert>
        </>
      )}
    </Box>
  );
}
