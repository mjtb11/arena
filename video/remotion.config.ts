import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setPixelFormat('yuv420p');
Config.setCodec('h264');
// In restricted sandboxes point this at a local chromium:
// Config.setBrowserExecutable('/tmp/chromium');
