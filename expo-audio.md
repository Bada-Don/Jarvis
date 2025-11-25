# Audio (expo-audio)

_A library that provides an API to implement audio playback and recording in apps._

Available on platforms android, ios, web, tvos

`expo-audio` is a cross-platform audio library for accessing the native audio capabilities of the device.

Note that audio automatically stops if headphones/bluetooth audio devices are disconnected.

## Installation

```bash
$ npx expo install expo-audio
```

If you are installing this in an existing React Native app, make sure to install `expo` in your project.

## Configuration in app config

You can configure `expo-audio` using its built-in [config plugin](https://docs.expo.dev/config-plugins/introduction/) if you use config plugins in your project ([Continuous Native Generation (CNG)](https://docs.expo.dev/workflow/continuous-native-generation/)). The plugin allows you to configure various properties that cannot be set at runtime and require building a new app binary to take effect. If your app does **not** use CNG, then you'll need to manually configure the library.

```json app.json
{
  "expo": {
    "plugins": [
      [
        "expo-audio",
        {
          "microphonePermission": "Allow $(PRODUCT_NAME) to access your microphone."
        }
      ]
    ]
  }
}
```

### Configurable properties
| Name | Default | Description |
| --- | --- | --- |
| `microphonePermission` | `"Allow $(PRODUCT_NAME) to access your microphone"` | Only for: ios. A string to set the `NSMicrophoneUsageDescription` permission message. Setting it to `false` will disable the permission. |
| `recordAudioAndroid` | `true` | Only for: android. A boolean that determines whether to enable the `RECORD_AUDIO` permission on Android. |
| `enableBackgroundRecording` | `false` | A boolean that determines whether to enable background audio recording. On Android, this adds foreground service permissions and displays a persistent notification during recording. On iOS, this adds the `audio` background mode. **Note:** Background recording can significantly impact battery life. |

## Usage

### Playing sounds

```jsx
import { View, StyleSheet, Button } from 'react-native';
import { useAudioPlayer } from 'expo-audio';

const audioSource = require('./assets/Hello.mp3');

export default function App() {
  const player = useAudioPlayer(audioSource);

  return (
    <View style={styles.container}>
      <Button title="Play Sound" onPress={() => player.play()} />
      <Button
        title="Replay Sound"
        onPress={() => {
          player.seekTo(0);
          player.play();
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    backgroundColor: '#ecf0f1',
    padding: 10,
  },
});
```

> **Info** **Note:** If you're migrating from [`expo-av`](av.mdx), you'll notice that `expo-audio` doesn't automatically reset the playback position when audio finishes. After [`play()`](#play), the player stays paused at the end of the sound. To play it again, call [`seekTo(seconds)`](#seektoseconds-tolerancemillisbefore-tolerancemillisafter) to reset the position — as shown in the example above.

### Recording sounds

```jsx
import { useState, useEffect } from 'react';
import { View, StyleSheet, Button } from 'react-native';
import {
  useAudioRecorder,
  AudioModule,
  RecordingPresets,
  setAudioModeAsync,
  useAudioRecorderState,
} from 'expo-audio';

export default function App() {
  const audioRecorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const recorderState = useAudioRecorderState(audioRecorder);

  const record = async () => {
    await audioRecorder.prepareToRecordAsync();
    audioRecorder.record();
  };

  const stopRecording = async () => {
    // The recording will be available on `audioRecorder.uri`.
    await audioRecorder.stop();
  };

  useEffect(() => {
    (async () => {
      const status = await AudioModule.requestRecordingPermissionsAsync();
      if (!status.granted) {
        Alert.alert('Permission to access microphone was denied');
      }

      setAudioModeAsync({
        playsInSilentMode: true,
        allowsRecording: true,
      });
    })();
  }, []);

  return (
    <View style={styles.container}>
      <Button
        title={recorderState.isRecording ? 'Stop Recording' : 'Start Recording'}
        onPress={recorderState.isRecording ? stopRecording : record}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    backgroundColor: '#ecf0f1',
    padding: 10,
  },
});
```

### Playing audio in background&ensp;<PlatformTags platforms={['ios']} />

On iOS, audio playback and recording in background is only available in standalone apps, and it requires some extra configuration.
On iOS, each background feature requires a special key in `UIBackgroundModes` array in your **Info.plist** file.
In standalone apps this array is empty by default, so to use background features you will need to add appropriate keys to your **app.json** configuration.

See an example of **app.json** that enables audio playback in background:

```json
{
  "expo": {
    ...
    "ios": {
      ...
      "infoPlist": {
        ...
        "UIBackgroundModes": [
          "audio"
        ]
      }
    }
  }
}
```

### Recording audio in background

> **warning** Background recording can significantly impact battery life. Only enable it when necessary for your app's functionality.

Background audio recording allows your app to continue recording when it moves to the background or when the device screen locks.

To enable background recording, use the config plugin in your [app config](https://docs.expo.dev/workflow/configuration/):

```json app.json
{
  "expo": {
    "plugins": [
      [
        "expo-audio",
        {
          "microphonePermission": "Allow $(PRODUCT_NAME) to record audio.",
          "enableBackgroundRecording": true
        }
      ]
    ]
  }
}
```

The above configuration automatically configures the required native settings:

- <PlatformTags platforms={['android']} /> Adds `FOREGROUND_SERVICE_MICROPHONE` and
  `POST_NOTIFICATIONS` permissions
- <PlatformTags platforms={['ios']} /> Adds the `audio` `UIBackgroundMode` capability

<ConfigReactNative>

If you're not using Continuous Native Generation ([CNG](https://docs.expo.dev/workflow/continuous-native-generation/)) (you're using native **android** and **ios** projects manually), then you need to configure following permissions in your native projects:

- For Android, add to **android/app/src/main/AndroidManifest.xml**:

  ```xml android/app/src/main/AndroidManifest.xml
  <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />
  <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
  ```

- For iOS, add to **ios/YourApp/Info.plist**:

  ```xml ios/YourApp/Info.plist
  <key>UIBackgroundModes</key>
  <array>
    <string>audio</string>
  </array>
  ```

</ConfigReactNative>

#### Usage

After configuring your app, enable background recording at runtime using [`setAudioModeAsync`](#audiosetaudiomodeasyncmode):

```jsx
import { setAudioModeAsync, useAudioRecorder, RecordingPresets } from 'expo-audio';

await setAudioModeAsync({
  playsInSilentMode: true,
  allowsRecording: true,
  allowsBackgroundRecording: true,
});

const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
await recorder.prepareToRecordAsync();
await recorder.record();

// Recording continues in background
```

<PlatformTags platforms={['android']} />

On Android, background recording requires a foreground service, which displays a persistent notification with the text "Recording audio" and a stop button. This notification cannot be dismissed while recording is active and automatically disappears when recording stops.

<PlatformTags platforms={['ios']} />

On iOS, background recording continues seamlessly when the app is in the background or the screen locks. No additional notifications or indicators are shown to the app user beyond the system status bar.

### Using the AudioPlayer directly

In most cases, the [`useAudioPlayer`](#useaudioplayersource-options) hook should be used to create a `AudioPlayer` instance. It manages the player's lifecycle and ensures that it is properly disposed of when the component is unmounted. However, in some advanced use cases, it might be necessary to create a `AudioPlayer` that does not get automatically destroyed when the component is unmounted.
In those cases, the `AudioPlayer` can be created using the [`createAudioPlayer`](#audiocreateaudioplayersource-updateinterval) function. You need to be aware of the risks that come with this approach, as it is your responsibility to call the [`release()`](../sdk/expo/#release) method when the player is no longer needed. If not handled properly, this approach may lead to memory leaks.

```tsx
import { createAudioPlayer } from 'expo-audio';
const player = createAudioPlayer(audioSource);
```

### Notes on web usage

- A MediaRecorder issue on Chrome produces WebM files missing the duration metadata. [See the open Chromium issue](https://bugs.chromium.org/p/chromium/issues/detail?id=642012).
- MediaRecorder encoding options and other configurations are inconsistent across browsers, utilizing a Polyfill such as [kbumsik/opus-media-recorder](https://github.com/kbumsik/opus-media-recorder) or [ai/audio-recorder-polyfill](https://github.com/ai/audio-recorder-polyfill) in your application will improve your experience. Any options passed to `prepareToRecordAsync` will be passed directly to the MediaRecorder API and as such the polyfill.
- Web browsers require sites to be served securely for them to listen to a mic. See [MediaDevices `getUserMedia()` security](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia#security) for more details.

## API

```js
import { useAudioPlayer, useAudioRecorder } from 'expo-audio';
```

## API: expo-audio

### AudioPlayer (*Class*)
#### Properties
- `currentTime` (number)
  The current position through the audio item in seconds.
- `duration` (number)
  The total duration of the audio in seconds.
- `id` (number)
  Unique identifier for the player object.
- `isAudioSamplingSupported` (boolean)
  Boolean value indicating whether audio sampling is supported on the platform.
- `isBuffering` (boolean)
  Boolean value indicating whether the player is buffering.
- `isLoaded` (boolean)
  Boolean value indicating whether the player is finished loading.
- `loop` (boolean)
  Boolean value indicating whether the player is currently looping.
- `muted` (boolean)
  Boolean value indicating whether the player is currently muted.
- `paused` (boolean)
  Boolean value indicating whether the player is currently paused.
- `playbackRate` (number)
  The current playback rate of the audio. It accepts different values depending on the platform:
  - **Android**: `0.1` to `2.0`
  - **iOS**: `0.0` to `2.0`
  - **Web**: Follows browser implementation
- `playing` (boolean)
  Boolean value indicating whether the player is currently playing.
- `shouldCorrectPitch` (boolean)
  A boolean describing if we are correcting the pitch for a changed rate.
- `volume` (number)
  The current volume of the audio.

  **Range:** `0.0` to `1.0`. For example, `0.0` is completely silent (0%), `0.5` is half volume (50%), and `1.0` is full volume (100%).
#### Methods
- `addListener(eventName: EventName, listener: indexedAccess): EventSubscription`
  Adds a listener for the given event name.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | EventName | - |
  | `listener` | indexedAccess | - |

- `clearLockScreenControls()`
  Removes this player from lock screen controls if it's currently active.
  This will clear the lock screen's now playing info.

- `emit(eventName: EventName, args: Parameters<indexedAccess>)`
  Synchronously calls all the listeners attached to that specific event.
  The event can include any number of arguments that will be passed to the listeners.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | EventName | - |
  | `args` | Parameters<indexedAccess> | - |

- `listenerCount(eventName: EventName): number`
  Returns a number of listeners added to the given event.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | EventName | - |

- `pause()`
  Pauses the player.

- `play()`
  Start playing audio.

- `release()`
  A function that detaches the JS and native objects to let the native object deallocate
  before the JS object gets deallocated by the JS garbage collector. Any subsequent calls to native
  functions of the object will throw an error as it is no longer associated with its native counterpart.

  In most cases, you should never need to use this function, except some specific performance-critical cases when
  manual memory management makes sense and the native object is known to exclusively retain some native memory
  (such as binary data or image bitmap). Before calling this function, you should ensure that nothing else will use
  this object later on. Shared objects created by React hooks are usually automatically released in the effect's cleanup phase,
  for example: `useVideoPlayer()` from `expo-video` and `useImage()` from `expo-image`.

- `remove()`
  Remove the player from memory to free up resources.

- `removeAllListeners(eventName: typeOperator)`
  Removes all listeners for the given event name.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | typeOperator | - |

- `removeListener(eventName: EventName, listener: indexedAccess)`
  Removes a listener for the given event name.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | EventName | - |
  | `listener` | indexedAccess | - |

- `replace(source: AudioSource)`
  Replaces the current audio source with a new one.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `source` | AudioSource | - |

- `seekTo(seconds: number, toleranceMillisBefore?: number, toleranceMillisAfter?: number): Promise<void>`
  Seeks the playback by the given number of seconds.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `seconds` | number | The number of seconds to seek by. |
  | `toleranceMillisBefore` *(optional)* | number | The tolerance allowed before the requested seek time, in milliseconds. iOS only. |
  | `toleranceMillisAfter` *(optional)* | number | The tolerance allowed after the requested seek time, in milliseconds. iOS only. |

- `setActiveForLockScreen(active: boolean, metadata?: AudioMetadata, options?: AudioLockScreenOptions)`
  Sets or removes this audio player as the active player for lock screen controls.
  Only one player can control the lock screen at a time.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `active` | boolean | Whether this player should be active for lock screen controls. |
  | `metadata` *(optional)* | AudioMetadata | Optional metadata to display on the lock screen (title, artist, album, artwork). |
  | `options` *(optional)* | AudioLockScreenOptions | Optional configuration to configure the lock screen controls. |

- `setPlaybackRate(rate: number, pitchCorrectionQuality?: PitchCorrectionQuality)`
  Sets the current playback rate of the audio.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `rate` | number | The playback rate of the audio. See [`playbackRate`](#playbackrate) property for detailed range information. |
  | `pitchCorrectionQuality` *(optional)* | PitchCorrectionQuality | The quality of the pitch correction. |

- `startObserving(eventName: EventName)`
  Function that is automatically invoked when the first listener for an event with the given name is added.
  Override it in a subclass to perform some additional setup once the event started being observed.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | EventName | - |

- `stopObserving(eventName: EventName)`
  Function that is automatically invoked when the last listener for an event with the given name is removed.
  Override it in a subclass to perform some additional cleanup once the event is no longer observed.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | EventName | - |

- `updateLockScreenMetadata(metadata: AudioMetadata)`
  Updates the metadata displayed on the lock screen for this player.
  This method only has an effect if this player is currently active for lock screen controls.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `metadata` | AudioMetadata | The metadata to display (title, artist, album, artwork). |

### AudioRecorder (*Class*)
#### Properties
- `currentTime` (number)
  The current length of the recording, in seconds.
- `id` (number)
  Unique identifier for the recorder object.
- `isRecording` (boolean)
  Boolean value indicating whether the recording is in progress.
- `uri` (null | string)
  The uri of the recording.
#### Methods
- `addListener(eventName: EventName, listener: indexedAccess): EventSubscription`
  Adds a listener for the given event name.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | EventName | - |
  | `listener` | indexedAccess | - |

- `emit(eventName: EventName, args: Parameters<indexedAccess>)`
  Synchronously calls all the listeners attached to that specific event.
  The event can include any number of arguments that will be passed to the listeners.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | EventName | - |
  | `args` | Parameters<indexedAccess> | - |

- `getAvailableInputs(): RecordingInput[]`
  Returns a list of available recording inputs. This method can only be called if the `Recording` has been prepared.
  Returns: A `Promise` that is fulfilled with an array of `RecordingInput` objects.

- `getCurrentInput(): Promise<RecordingInput>`
  Returns the currently-selected recording input. This method can only be called if the `Recording` has been prepared.
  Returns: A `Promise` that is fulfilled with a `RecordingInput` object.

- `getStatus(): RecorderState`
  Status of the current recording.

- `listenerCount(eventName: EventName): number`
  Returns a number of listeners added to the given event.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | EventName | - |

- `pause()`
  Pause the recording.

- `prepareToRecordAsync(options?: Partial<RecordingOptions>): Promise<void>`
  Prepares the recording for recording.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `options` *(optional)* | Partial<RecordingOptions> | - |

- `record(options?: RecordingStartOptions)`
  Starts the recording.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `options` *(optional)* | RecordingStartOptions | Optional recording configuration options. |

- `recordForDuration(seconds: number)`
  Stops the recording once the specified time has elapsed.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `seconds` | number | The time in seconds to stop recording at. |

- `release()`
  A function that detaches the JS and native objects to let the native object deallocate
  before the JS object gets deallocated by the JS garbage collector. Any subsequent calls to native
  functions of the object will throw an error as it is no longer associated with its native counterpart.

  In most cases, you should never need to use this function, except some specific performance-critical cases when
  manual memory management makes sense and the native object is known to exclusively retain some native memory
  (such as binary data or image bitmap). Before calling this function, you should ensure that nothing else will use
  this object later on. Shared objects created by React hooks are usually automatically released in the effect's cleanup phase,
  for example: `useVideoPlayer()` from `expo-video` and `useImage()` from `expo-image`.

- `removeAllListeners(eventName: 'recordingStatusUpdate')`
  Removes all listeners for the given event name.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | 'recordingStatusUpdate' | - |

- `removeListener(eventName: EventName, listener: indexedAccess)`
  Removes a listener for the given event name.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | EventName | - |
  | `listener` | indexedAccess | - |

- `setInput(inputUid: string)`
  Sets the current recording input.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `inputUid` | string | The uid of a `RecordingInput`. |
  Returns: A `Promise` that is resolved if successful or rejected if not.

- `startObserving(eventName: EventName)`
  Function that is automatically invoked when the first listener for an event with the given name is added.
  Override it in a subclass to perform some additional setup once the event started being observed.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | EventName | - |

- `startRecordingAtTime(seconds: number)`
  Starts the recording at the given time.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `seconds` | number | The time in seconds to start recording at. |

- `stop(): Promise<void>`
  Stop the recording.

- `stopObserving(eventName: EventName)`
  Function that is automatically invoked when the last listener for an event with the given name is removed.
  Override it in a subclass to perform some additional cleanup once the event is no longer observed.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `eventName` | EventName | - |

### Hooks

#### useAudioPlayer (*Function*)
- `useAudioPlayer(source: AudioSource, options: AudioPlayerOptions): AudioPlayer`
  Creates an `AudioPlayer` instance that automatically releases when the component unmounts.

  This hook manages the player's lifecycle and ensures it's properly disposed when no longer needed.
  The player will start loading the audio source immediately upon creation.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `source` | AudioSource | The audio source to load. Can be a local asset via `require()`, a remote URL, or null for no initial source. |
  | `options` | AudioPlayerOptions | Audio player configuration options. |
  Returns: An `AudioPlayer` instance that's automatically managed by the component lifecycle.
  Example:
  ```tsx
  import { useAudioPlayer } from 'expo-audio';

  function MyComponent() {
    const player = useAudioPlayer(require('./sound.mp3'));

    return (
      <Button title="Play" onPress={() => player.play()} />
    );
  }
  ```

#### useAudioPlayerStatus (*Function*)
- `useAudioPlayerStatus(player: AudioPlayer): AudioStatus`
  Hook that provides real-time playback status updates for an `AudioPlayer`.

  This hook automatically subscribes to playback status changes and returns the current status.
  The status includes information about playback state, current time, duration, loading state, and more.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `player` | AudioPlayer | The `AudioPlayer` instance to monitor. |
  Returns: The current `AudioStatus` object containing playback information.
  Example:
  ```tsx
  import { useAudioPlayer, useAudioPlayerStatus } from 'expo-audio';

  function PlayerComponent() {
    const player = useAudioPlayer(require('./sound.mp3'));
    const status = useAudioPlayerStatus(player);

    return (
      <View>
        <Text>Playing: {status.playing ? 'Yes' : 'No'}</Text>
        <Text>Current Time: {status.currentTime}s</Text>
        <Text>Duration: {status.duration}s</Text>
      </View>
    );
  }
  ```

#### useAudioRecorder (*Function*)
- `useAudioRecorder(options: RecordingOptions, statusListener?: (status: RecordingStatus) => void): AudioRecorder`
  Hook that creates an `AudioRecorder` instance for recording audio.

  This hook manages the recorder's lifecycle and ensures it's properly disposed when no longer needed.
  The recorder is automatically prepared with the provided options and can be used to record audio.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `options` | RecordingOptions | Recording configuration options including format, quality, sample rate, etc. |
  | `statusListener` *(optional)* | (status: RecordingStatus) => void | Optional callback function that receives recording status updates. |
  Returns: An `AudioRecorder` instance that's automatically managed by the component lifecycle.
  Example:
  ```tsx
  import { useAudioRecorder, RecordingPresets } from 'expo-audio';

  function RecorderComponent() {
    const recorder = useAudioRecorder(
      RecordingPresets.HIGH_QUALITY,
      (status) => console.log('Recording status:', status)
    );

    const startRecording = async () => {
      await recorder.prepareToRecordAsync();
      recorder.record();
    };

    return (
      <Button title="Start Recording" onPress={startRecording} />
    );
  }
  ```

#### useAudioRecorderState (*Function*)
- `useAudioRecorderState(recorder: AudioRecorder, interval: number): RecorderState`
  Hook that provides real-time recording state updates for an `AudioRecorder`.

  This hook polls the recorder's status at regular intervals and returns the current recording state.
  Use this when you need to monitor the recording status without setting up a status listener.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `recorder` | AudioRecorder | The `AudioRecorder` instance to monitor. |
  | `interval` | number | How often (in milliseconds) to poll the recorder's status. Defaults to 500ms. |
  Returns: The current `RecorderState` containing recording information.
  Example:
  ```tsx
  import { useAudioRecorder, useAudioRecorderState, RecordingPresets } from 'expo-audio';

  function RecorderStatusComponent() {
    const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
    const state = useAudioRecorderState(recorder);

    return (
      <View>
        <Text>Recording: {state.isRecording ? 'Yes' : 'No'}</Text>
        <Text>Duration: {Math.round(state.durationMillis / 1000)}s</Text>
        <Text>Can Record: {state.canRecord ? 'Yes' : 'No'}</Text>
      </View>
    );
  }
  ```

### Audio Methods

#### createAudioPlayer (*Function*)
- `createAudioPlayer(source: AudioSource, options: AudioPlayerOptions): AudioPlayer`
  Creates an instance of an `AudioPlayer` that doesn't release automatically.

  > **info** For most use cases you should use the [`useAudioPlayer`](#useaudioplayer) hook instead.
  > See the [Using the `AudioPlayer` directly](#using-the-audioplayer-directly) section for more details.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `source` | AudioSource | The audio source to load. |
  | `options` | AudioPlayerOptions | Audio player configuration options. |

#### getRecordingPermissionsAsync (*Function*)
- `getRecordingPermissionsAsync(): Promise<PermissionResponse>`
  Checks the current status of recording permissions without requesting them.

  This function returns the current permission status for microphone access
  without triggering a permission request dialog. Use this to check permissions
  before deciding whether to call `requestRecordingPermissionsAsync()`.
  Returns: A Promise that resolves to a `PermissionResponse` object containing the current permission status.
  Example:
  ```tsx
  import { getRecordingPermissionsAsync, requestRecordingPermissionsAsync } from 'expo-audio';

  const ensureRecordingPermissions = async () => {
    const { status } = await getRecordingPermissionsAsync();

    if (status !== 'granted') {
      // Permission not granted, request it
      const { granted } = await requestRecordingPermissionsAsync();
      return granted;
    }

    return true; // Already granted
  };
  ```

#### requestRecordingPermissionsAsync (*Function*)
- `requestRecordingPermissionsAsync(): Promise<PermissionResponse>`
  Requests permission to record audio from the microphone.

  This function prompts the user for microphone access permission, which is required
  for audio recording functionality. On iOS, this will show the system permission dialog.
  On Android, this requests the `RECORD_AUDIO` permission.
  Returns: A Promise that resolves to a `PermissionResponse` object containing the permission status.
  Example:
  ```tsx
  import { requestRecordingPermissionsAsync } from 'expo-audio';

  const checkPermissions = async () => {
    const { status, granted } = await requestRecordingPermissionsAsync();

    if (granted) {
      console.log('Recording permission granted');
    } else {
      console.log('Recording permission denied:', status);
    }
  };
  ```

#### setAudioModeAsync (*Function*)
- `setAudioModeAsync(mode: Partial<AudioMode>): Promise<void>`
  Configures the global audio behavior and session settings.

  This function allows you to control how your app's audio interacts with other apps,
  background playback behavior, audio routing, and interruption handling.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `mode` | Partial<AudioMode> | Partial audio mode configuration object. Only specified properties will be updated. |
  Returns: A Promise that resolves when the audio mode has been applied.
  Example:
  ```tsx
  import { setAudioModeAsync } from 'expo-audio';

  // Configure audio for background playback
  await setAudioModeAsync({
    playsInSilentMode: true,
    shouldPlayInBackground: true,
    interruptionModeAndroid: 'duckOthers',
    interruptionMode: 'mixWithOthers'
  });

  // Configure audio for recording
  await setAudioModeAsync({
    allowsRecording: true,
    playsInSilentMode: true
  });
  ```

#### setIsAudioActiveAsync (*Function*)
- `setIsAudioActiveAsync(active: boolean): Promise<void>`
  Enables or disables the audio subsystem globally.

  When set to `false`, this will pause all audio playback and prevent new audio from playing.
  This is useful for implementing app-wide audio controls or responding to system events.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `active` | boolean | Whether audio should be active (`true`) or disabled (`false`). |
  Returns: A Promise that resolves when the audio state has been updated.
  Example:
  ```tsx
  import { setIsAudioActiveAsync } from 'expo-audio';

  // Disable all audio when app goes to background
  const handleAppStateChange = async (nextAppState) => {
    if (nextAppState === 'background') {
      await setIsAudioActiveAsync(false);
    } else if (nextAppState === 'active') {
      await setIsAudioActiveAsync(true);
    }
  };
  ```

### Event Subscriptions

#### useAudioSampleListener (*Function*)
- `useAudioSampleListener(player: AudioPlayer, listener: (data: AudioSample) => void)`
  Hook that sets up audio sampling for an `AudioPlayer` and calls a listener with audio data.

  This hook enables audio sampling on the player (if supported) and subscribes to audio sample updates.
  Audio sampling provides real-time access to audio waveform data for visualization or analysis.

  > **Note:** Audio sampling requires `RECORD_AUDIO` permission on Android and is not supported on all platforms.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `player` | AudioPlayer | The `AudioPlayer` instance to sample audio from. |
  | `listener` | (data: AudioSample) => void | Function called with each audio sample containing waveform data. |
  Example:
  ```tsx
  import { useEffect } from 'react';
  import { useAudioPlayer, useAudioSampleListener, requestRecordingPermissionsAsync } from 'expo-audio';

  function AudioVisualizerComponent() {
    const player = useAudioPlayer(require('./music.mp3'));

    // if required on Android, request recording permissions
    useEffect(() => {
      async function requestPermission() {
        const { granted } = await requestRecordingPermissionsAsync();
        if (granted) {
          console.log("Permission granted");
        }
      }

      requestPermission();
     }, []);

    useAudioSampleListener(player, (sample) => {
      // Use sample.channels array for audio visualization
      console.log('Audio sample:', sample.channels[0].frames);
    });

    return <AudioWaveform player={player} />;
  }
  ```

### Types

#### AndroidAudioEncoder (*Type*)
Audio encoder options for Android recording.

Specifies the audio codec used to encode recorded audio on Android.
Different encoders offer different quality, compression, and compatibility trade-offs.
Available on platform: android
Type: 'default' | 'amr_nb' | 'amr_wb' | 'aac' | 'he_aac' | 'aac_eld'

#### AndroidOutputFormat (*Type*)
Audio output format options for Android recording.

Specifies the container format for recorded audio files on Android.
Different formats have different compatibility and compression characteristics.
Available on platform: android
Type: 'default' | '3gp' | 'mpeg4' | 'amrnb' | 'amrwb' | 'aac_adts' | 'mpeg2ts' | 'webm'

#### AudioEvents (*Type*)
Event types that an `AudioPlayer` can emit.

These events allow you to listen for changes in playback state and receive real-time audio data.
Use `player.addListener()` to subscribe to these events.
| Property | Type | Description |
| --- | --- | --- |
| `audioSampleUpdate` | - | - |
| `playbackStatusUpdate` | - | - |

#### AudioLoadOptions (*Type*)
Type: AudioPlayerOptions

#### AudioLockScreenOptions (*Type*)
Options for configuring which playback controls should be displayed on the lock screen.
| Property | Type | Description |
| --- | --- | --- |
| `showSeekBackward` *(optional)* | boolean | Whether the seek backward button should be displayed on the lock screen. |
| `showSeekForward` *(optional)* | boolean | Whether the seek forward button should be displayed on the lock screen. |

#### AudioMetadata (*Type*)
| Property | Type | Description |
| --- | --- | --- |
| `albumTitle` *(optional)* | string | - |
| `artist` *(optional)* | string | - |
| `artworkUrl` *(optional)* | string | - |
| `title` *(optional)* | string | - |

#### AudioMode (*Type*)
| Property | Type | Description |
| --- | --- | --- |
| `allowsRecording` | boolean | Whether the audio session allows recording. Default: `false` Available on platform: ios |
| `interruptionMode` | InterruptionMode | Determines how the audio session interacts with other sessions. Available on platform: ios |
| `interruptionModeAndroid` | InterruptionModeAndroid | Determines how the audio session interacts with other sessions on Android. Available on platform: android |
| `playsInSilentMode` | boolean | Determines if audio playback is allowed when the device is in silent mode. Available on platform: ios |
| `shouldPlayInBackground` | boolean | Whether the audio session stays active when the app moves to the background. Default: `false` |
| `shouldRouteThroughEarpiece` | boolean | Whether the audio should route through the earpiece. Available on platform: android |

#### AudioPlayerOptions (*Type*)
Options for configuring audio player behavior.
| Property | Type | Description |
| --- | --- | --- |
| `crossOrigin` *(optional)* | 'anonymous' \| 'use-credentials' | Determines the [cross origin policy](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/crossorigin) used by the underlying native view on web.<br>If `undefined` (default), does not use CORS at all. If set to `'anonymous'`, the audio will be loaded with CORS enabled.<br>Note that some audio may not play if CORS is enabled, depending on the CDN settings.<br>If you encounter issues, consider adjusting the `crossOrigin` property. Default: `undefined` Available on platform: web |
| `downloadFirst` *(optional)* | boolean | If set to `true`, the system will attempt to download the resource to the device before loading.<br>This value defaults to `false`.<br><br>Works with:<br>- Local assets from `require('path/to/file')`<br>- Remote HTTP/HTTPS URLs<br>- Asset objects<br><br>When enabled, this ensures the audio file is fully downloaded before playback begins.<br>This can improve playback performance and reduce buffering, especially for users<br>managing multiple audio players simultaneously.<br><br>On Android and iOS, this will download the audio file to the device's tmp directory before playback begins.<br>The system will purge the file at its discretion.<br><br>On web, this will download the audio file to the user's device memory and make it available for the user to play.<br>The system will usually purge the file from memory after a reload or on memory pressure.<br>On web, CORS restrictions apply to the blob url, so you need to make sure the server returns the `Access-Control-Allow-Origin` header. Available on platforms: ios, web, android |
| `keepAudioSessionActive` *(optional)* | boolean | If set to `true`, the audio session will not be deactivated when this player pauses or finishes playback.<br>This prevents interrupting other audio sources (like videos) when the audio ends.<br><br>Useful for sound effects that should not interfere with ongoing video playback or other audio.<br>The audio session for this player will not be deactivated automatically when the player finishes playback.<br><br>> **Note:** If needed, you can manually deactivate the audio session using `setIsAudioActiveAsync(false)`. Default: `false` Available on platform: ios |
| `updateInterval` *(optional)* | number | How often (in milliseconds) to emit playback status updates. Defaults to 500ms. Default: `500ms` Available on platforms: ios, android, web |

#### AudioSample (*Type*)
Represents a single audio sample containing waveform data from all audio channels.

Audio samples are provided in real-time when audio sampling is enabled on an `AudioPlayer`.
Each sample contains the raw PCM audio data for all channels (mono has 1 channel, stereo has 2).
This data can be used for audio visualization, analysis, or processing.
| Property | Type | Description |
| --- | --- | --- |
| `channels` | AudioSampleChannel[] | Array of audio channels, each containing PCM frame data. Stereo audio will have 2 channels (left/right). |
| `timestamp` | number | Timestamp of this sample relative to the audio track's timeline, in seconds. |

#### AudioSampleChannel (*Type*)
Represents audio data for a single channel (for example, left or right in stereo audio).

Contains the raw PCM (Pulse Code Modulation) audio frames for this channel.
Frame values are normalized between -1.0 and 1.0, where 0 represents silence.
| Property | Type | Description |
| --- | --- | --- |
| `frames` | number[] | Array of PCM audio frame values, each between -1.0 and 1.0. |

#### AudioSource (*Type*)
| Property | Type | Description |
| --- | --- | --- |
| `assetId` *(optional)* | number | The asset ID of a local audio asset, acquired with the `require` function.<br>This property is exclusive with the `uri` property. When both are present, the `assetId` will be ignored. |
| `headers` *(optional)* | Record<string, string> | An object representing the HTTP headers to send along with the request for a remote audio source.<br>On web requires the `Access-Control-Allow-Origin` header returned by the server to include the current domain. |
| `uri` *(optional)* | string | A string representing the resource identifier for the audio,<br>which could be an HTTPS address, a local file path, or the name of a static audio file resource. |

#### AudioStatus (*Type*)
Comprehensive status information for an `AudioPlayer`.

This object contains all the current state information about audio playback,
including playback position, duration, loading state, and playback settings.
Used by `useAudioPlayerStatus()` to provide real-time status updates.
| Property | Type | Description |
| --- | --- | --- |
| `currentTime` | number | Current playback position in seconds. |
| `didJustFinish` | boolean | Whether the audio just finished playing. |
| `duration` | number | Total duration of the audio in seconds, or 0 if not yet determined. |
| `id` | number | Unique identifier for the player instance. |
| `isBuffering` | boolean | Whether the player is currently buffering data. |
| `isLoaded` | boolean | Whether the audio has finished loading and is ready to play. |
| `loop` | boolean | Whether the audio is set to loop when it reaches the end. |
| `mute` | boolean | Whether the player is currently muted. |
| `playbackRate` | number | Current playback rate (1.0 = normal speed). |
| `playbackState` | string | String representation of the player's internal playback state. |
| `playing` | boolean | Whether the audio is currently playing. |
| `reasonForWaitingToPlay` | string | Reason why the player is waiting to play (if applicable). |
| `shouldCorrectPitch` | boolean | Whether pitch correction is enabled for rate changes. Default: `true` |
| `timeControlStatus` | string | String representation of the player's time control status (playing/paused/waiting). |

#### BitRateStrategy (*Type*)
Bit rate strategies for audio encoding.

Determines how the encoder manages bit rate during recording, affecting
file size consistency and quality characteristics.
Type: 'constant' | 'longTermAverage' | 'variableConstrained' | 'variable'

#### InterruptionMode (*Type*)
Audio interruption behavior modes for iOS.

Controls how your app's audio interacts with other apps' audio when interruptions occur.
This affects what happens when phone calls, notifications, or other apps play audio.
Available on platform: ios
Type: 'mixWithOthers' | 'doNotMix' | 'duckOthers'

#### InterruptionModeAndroid (*Type*)
Audio interruption behavior modes for Android.

Controls how your app's audio interacts with other apps' audio on Android.
Note that Android doesn't support 'mixWithOthers' mode; audio focus is more strictly managed.
Available on platform: android
Type: 'doNotMix' | 'duckOthers'

#### PermissionExpiration (*Type*)
Permission expiration time. Currently, all permissions are granted permanently.
Type: 'never' | number

#### PermissionResponse (*Type*)
An object obtained by permissions get and request functions.
| Property | Type | Description |
| --- | --- | --- |
| `canAskAgain` | boolean | Indicates if user can be asked again for specific permission.<br>If not, one should be directed to the Settings app<br>in order to enable/disable the permission. |
| `expires` | PermissionExpiration | Determines time when the permission expires. |
| `granted` | boolean | A convenience boolean that indicates if the permission is granted. |
| `status` | PermissionStatus | Determines the status of the permission. |

#### PitchCorrectionQuality (*Type*)
Pitch correction quality settings for audio playback rate changes.

When changing playback rate, pitch correction can be applied to maintain the original pitch.
Different quality levels offer trade-offs between processing power and audio quality.
Available on platform: ios
Type: 'low' | 'medium' | 'high'

#### RecorderState (*Type*)
Current state information for an `AudioRecorder`.

This object contains detailed information about the recorder's current state,
including recording status, duration, and technical details. This is what you get
when calling `recorder.getStatus()` or using `useAudioRecorderState()`.
| Property | Type | Description |
| --- | --- | --- |
| `canRecord` | boolean | Whether the recorder is ready and able to record. |
| `durationMillis` | number | Duration of the current recording in milliseconds. |
| `isRecording` | boolean | Whether recording is currently in progress. |
| `mediaServicesDidReset` | boolean | Whether the media services have been reset (typically indicates a system interruption). |
| `metering` *(optional)* | number | Current audio level/volume being recorded (if metering is enabled). |
| `url` | string \| null | File URL where the recording will be saved, if available. |

#### RecordingEvents (*Type*)
Event types that an `AudioRecorder` can emit.

These events are used internally by `expo-audio` hooks to provide real-time status updates.
Use `useAudioRecorderState()` or the `statusListener` parameter in `useAudioRecorder()` instead of subscribing directly.
| Property | Type | Description |
| --- | --- | --- |
| `recordingStatusUpdate` | (status: RecordingStatus) => void | Fired when the recorder's status changes (start/stop/pause/error, and so on). |

#### RecordingInput (*Type*)
Represents an available audio input device for recording.

This type describes audio input sources like built-in microphones, external microphones,
or other audio input devices that can be used for recording. Each input has an identifying
information that can be used to select the preferred recording source.
| Property | Type | Description |
| --- | --- | --- |
| `name` | string | Human-readable name of the audio input device. |
| `type` | string | Type or category of the input device (for example, 'Built-in Microphone', 'External Microphone'). |
| `uid` | string | Unique identifier for the input device, used to select the input ('Built-in Microphone', 'External Microphone') for recording. |

#### RecordingOptions (*Type*)
| Property | Type | Description |
| --- | --- | --- |
| `android` | RecordingOptionsAndroid | Recording options for the Android platform. Available on platform: android |
| `bitRate` | number | The desired bit rate. |
| `extension` | string | The desired file extension. |
| `ios` | RecordingOptionsIos | Recording options for the iOS platform. Available on platform: ios |
| `isMeteringEnabled` *(optional)* | boolean | A boolean that determines whether audio level information will be part of the status object under the "metering" key. |
| `numberOfChannels` | number | The desired number of channels. |
| `sampleRate` | number | The desired sample rate. |
| `web` *(optional)* | RecordingOptionsWeb | Recording options for the Web platform. Available on platform: web |

#### RecordingOptionsAndroid (*Type*)
Recording configuration options specific to Android.

Android recording uses `MediaRecorder` with options for format, encoder, and file constraints.
These settings control the output format and quality characteristics.
Available on platform: android
| Property | Type | Description |
| --- | --- | --- |
| `audioEncoder` | AndroidAudioEncoder | The desired audio encoder. See the [`AndroidAudioEncoder`](#androidaudioencoder) enum for all valid values. |
| `audioSource` *(optional)* | RecordingSource | The desired audio Source. See the [`AndroidAudioSource`](#androidaudiosource) enum for all valid values. |
| `extension` *(optional)* | string | The desired file extension. |
| `maxFileSize` *(optional)* | number | The desired maximum file size in bytes, after which the recording will stop (but `stopAndUnloadAsync()` must still<br>be called after this point). |
| `outputFormat` | AndroidOutputFormat | The desired file format. See the [`AndroidOutputFormat`](#androidoutputformat) enum for all valid values. |
| `sampleRate` *(optional)* | number | The desired sample rate. |

#### RecordingOptionsIos (*Type*)
Recording configuration options specific to iOS.

iOS recording uses `AVAudioRecorder` with extensive format and quality options.
These settings provide fine-grained control over the recording characteristics.
Available on platform: ios
| Property | Type | Description |
| --- | --- | --- |
| `audioQuality` | AudioQuality \| number | The desired audio quality. See the [`AudioQuality`](#audioquality) enum for all valid values. |
| `bitDepthHint` *(optional)* | number | The desired bit depth hint. |
| `bitRateStrategy` *(optional)* | number | The desired bit rate strategy. See the next section for an enumeration of all valid values of `bitRateStrategy`. |
| `extension` *(optional)* | string | The desired file extension. |
| `linearPCMBitDepth` *(optional)* | number | The desired PCM bit depth. |
| `linearPCMIsBigEndian` *(optional)* | boolean | A boolean describing if the PCM data should be formatted in big endian. |
| `linearPCMIsFloat` *(optional)* | boolean | A boolean describing if the PCM data should be encoded in floating point or integral values. |
| `outputFormat` *(optional)* | string \| IOSOutputFormat \| number | The desired file format. See the [`IOSOutputFormat`](#iosoutputformat) enum for all valid values. |
| `sampleRate` *(optional)* | number | The desired sample rate. |

#### RecordingOptionsWeb (*Type*)
Recording options for the web.

Web recording uses the `MediaRecorder` API, which has different capabilities
compared to native platforms. These options map directly to `MediaRecorder` settings.
Available on platform: web
| Property | Type | Description |
| --- | --- | --- |
| `bitsPerSecond` *(optional)* | number | Target bits per second for the recording. |
| `mimeType` *(optional)* | string | MIME type for the recording (for example, 'audio/webm', 'audio/mp4'). |

#### RecordingSource (*Type*)
Recording source for android.

An audio source defines both a default physical source of audio signal, and a recording configuration.

- `camcorder`: Microphone audio source tuned for video recording, with the same orientation as the camera if available.
- `default`: The default audio source.
- `mic`: Microphone audio source.
- `unprocessed`: Microphone audio source tuned for unprocessed (raw) sound if available, behaves like `default` otherwise.
- `voice_communication`: Microphone audio source tuned for voice communications such as VoIP. It will for instance take advantage of echo cancellation or automatic gain control if available.
- `voice_performance`: Source for capturing audio meant to be processed in real time and played back for live performance (e.g karaoke). The capture path will minimize latency and coupling with playback path.
- `voice_recognition`: Microphone audio source tuned for voice recognition.
Available on platform: android
Type: 'camcorder' | 'default' | 'mic' | 'remote_submix' | 'unprocessed' | 'voice_communication' | 'voice_performance' | 'voice_recognition'

#### RecordingStartOptions (*Type*)
Options for controlling how audio recording is started.
| Property | Type | Description |
| --- | --- | --- |
| `atTime` *(optional)* | number | The time in seconds to wait before starting the recording.<br>If not provided, recording starts immediately.<br><br>**Platform behavior:**<br>- Android: Ignored, recording starts immediately<br>- iOS: Uses native AVAudioRecorder.record(atTime:) for precise timing.<br>- Web: Ignored, recording starts immediately<br><br>> **warning** On iOS, the recording process starts immediately (you'll see status updates),<br>but actual audio capture begins after the specified delay. This is not a countdown, since<br>the recorder is active but silent during the delay period. Available on platform: ios |
| `forDuration` *(optional)* | number | The duration in seconds after which recording should automatically stop.<br>If not provided, recording continues until manually stopped. Available on platforms: ios, android, web |

#### RecordingStatus (*Type*)
Status information for recording operations from the event system.

This type represents the status data emitted by `recordingStatusUpdate` events.
It contains high-level information about the recording session and any errors.
Used internally by the event system. Most users should use `useAudioRecorderState()` instead.
| Property | Type | Description |
| --- | --- | --- |
| `error` | string \| null | Error message if an error occurred, `null` otherwise. |
| `hasError` | boolean | Whether an error occurred during recording. |
| `id` | number | Unique identifier for the recording session. |
| `isFinished` | boolean | Whether the recording has finished (stopped). |
| `url` | string \| null | File URL of the completed recording, if available. |

### Constants

#### RecordingPresets (*Constant*)
Constant which contains definitions of the two preset examples of `RecordingOptions`, as implemented in the Audio SDK.

# `HIGH_QUALITY`
```ts
RecordingPresets.HIGH_QUALITY = {
 extension: '.m4a',
  sampleRate: 44100,
  numberOfChannels: 2,
  bitRate: 128000,
  android: {
    outputFormat: 'mpeg4',
    audioEncoder: 'aac',
  },
  ios: {
    outputFormat: IOSOutputFormat.MPEG4AAC,
    audioQuality: AudioQuality.MAX,
    linearPCMBitDepth: 16,
    linearPCMIsBigEndian: false,
    linearPCMIsFloat: false,
  },
  web: {
    mimeType: 'audio/webm',
    bitsPerSecond: 128000,
  },
};
```

# `LOW_QUALITY`
```ts
RecordingPresets.LOW_QUALITY = {
  extension: '.m4a',
  sampleRate: 44100,
  numberOfChannels: 2,
  bitRate: 64000,
  android: {
    extension: '.3gp',
    outputFormat: '3gp',
    audioEncoder: 'amr_nb',
  },
  ios: {
    audioQuality: AudioQuality.MIN,
    outputFormat: IOSOutputFormat.MPEG4AAC,
    linearPCMBitDepth: 16,
    linearPCMIsBigEndian: false,
    linearPCMIsFloat: false,
  },
  web: {
    mimeType: 'audio/webm',
    bitsPerSecond: 128000,
  },
};
```
- `RecordingPresets` ({ HIGH_QUALITY: RecordingOptions; LOW_QUALITY: RecordingOptions }) — Constant which contains definitions of the two preset examples of `RecordingOptions`, as implemented in the Audio SDK.

# `HIGH_QUALITY`
```ts
RecordingPresets.HIGH_QUALITY = {
 extension: '.m4a',
  sampleRate: 44100,
  numberOfChannels: 2,
  bitRate: 128000,
  android: {
    outputFormat: 'mpeg4',
    audioEncoder: 'aac',
  },
  ios: {
    outputFormat: IOSOutputFormat.MPEG4AAC,
    audioQuality: AudioQuality.MAX,
    linearPCMBitDepth: 16,
    linearPCMIsBigEndian: false,
    linearPCMIsFloat: false,
  },
  web: {
    mimeType: 'audio/webm',
    bitsPerSecond: 128000,
  },
};
```

# `LOW_QUALITY`
```ts
RecordingPresets.LOW_QUALITY = {
  extension: '.m4a',
  sampleRate: 44100,
  numberOfChannels: 2,
  bitRate: 64000,
  android: {
    extension: '.3gp',
    outputFormat: '3gp',
    audioEncoder: 'amr_nb',
  },
  ios: {
    audioQuality: AudioQuality.MIN,
    outputFormat: IOSOutputFormat.MPEG4AAC,
    linearPCMBitDepth: 16,
    linearPCMIsBigEndian: false,
    linearPCMIsFloat: false,
  },
  web: {
    mimeType: 'audio/webm',
    bitsPerSecond: 128000,
  },
};
```  = ...

### Enums

#### AudioQuality (*Enum*)
Audio quality levels for recording.

Predefined quality levels that balance file size and audio fidelity.
Higher quality levels produce better sound but larger files and require more processing power.
#### Members
- `HIGH` — High quality: good fidelity, larger file size.
- `LOW` — Low quality: good for voice recordings where file size matters.
- `MAX` — Maximum quality: best fidelity, largest file size.
- `MEDIUM` — Medium quality: balanced option for most use cases.
- `MIN` — Minimum quality: smallest file size, lowest fidelity.

#### IOSOutputFormat (*Enum*)
Audio output format options for iOS recording.

Comprehensive enum of audio formats supported by iOS for recording.
Each format has different characteristics in terms of quality, file size, and compatibility.
Some formats like LINEARPCM offer the highest quality but larger file sizes,
while compressed formats like AAC provide good quality with smaller files.
Available on platform: ios
#### Members
- `60958AC3`
- `AC3`
- `AES3`
- `ALAW`
- `AMR`
- `AMR_WB`
- `APPLEIMA4`
- `APPLELOSSLESS`
- `AUDIBLE`
- `DVIINTELIMA`
- `ENHANCEDAC3`
- `ILBC`
- `LINEARPCM`
- `MACE3`
- `MACE6`
- `MICROSOFTGSM`
- `MPEG4AAC`
- `MPEG4AAC_ELD`
- `MPEG4AAC_ELD_SBR`
- `MPEG4AAC_ELD_V2`
- `MPEG4AAC_HE`
- `MPEG4AAC_HE_V2`
- `MPEG4AAC_LD`
- `MPEG4AAC_SPATIAL`
- `MPEG4CELP`
- `MPEG4HVXC`
- `MPEG4TWINVQ`
- `MPEGLAYER1`
- `MPEGLAYER2`
- `MPEGLAYER3`
- `QDESIGN`
- `QDESIGN2`
- `QUALCOMM`
- `ULAW`

#### PermissionStatus (*Enum*)
#### Members
- `DENIED` — User has denied the permission.
- `GRANTED` — User has granted the permission.
- `UNDETERMINED` — User hasn't granted or denied the permission yet.