# ImagePicker

_A library that provides access to the system's UI for selecting images and videos from the phone's library or taking a photo with the camera._

Available on platforms android, ios, web

`expo-image-picker` provides access to the system's UI for selecting images and videos from the phone's library or taking a photo with the camera.

<ContentSpotlight file="sdk/imagepicker.mp4" loop={false} />

## Installation

```bash
$ npx expo install expo-image-picker
```

If you are installing this in an existing React Native app, make sure to install `expo` in your project.

#### Known issues&ensp;<PlatformTags platforms={['ios']} />

On iOS, when an image (usually of a [higher resolution](http://www.openradar.me/49866214)) is picked from the camera roll, the result of the cropped image gives the wrong value for the cropped rectangle in some cases. Unfortunately, this issue is with the underlying `UIImagePickerController` due to a bug in the closed-source tools built into iOS.

## Configuration in app config

You can configure `expo-image-picker` using its built-in [config plugin](https://docs.expo.dev/config-plugins/introduction/) if you use config plugins in your project ([Continuous Native Generation (CNG)](https://docs.expo.dev/workflow/continuous-native-generation/)). The plugin allows you to configure various properties that cannot be set at runtime and require building a new app binary to take effect. If your app does **not** use CNG, then you'll need to manually configure the library.

```json app.json
{
  "expo": {
    "plugins": [
      [
        "expo-image-picker",
        {
          "photosPermission": "The app accesses your photos to let you share them with your friends."
          "colors": {
            "cropToolbarColor": "#000000",
          },
          "dark": {
            "colors": {
              "cropToolbarColor": "#000000",
            }
          }
        }
      ]
    ]
  }
}
```

### Configurable properties
| Name | Default | Description |
| --- | --- | --- |
| `photosPermission` | `"Allow $(PRODUCT_NAME) to access your photos"` | Only for: ios. A string to set the `NSPhotoLibraryUsageDescription` permission message. |
| `cameraPermission` | `"Allow $(PRODUCT_NAME) to access your camera"` | Only for: ios. A string to set the `NSCameraUsageDescription` permission message. |
| `microphonePermission` | `"Allow $(PRODUCT_NAME) to access your microphone"` | Only for: ios. A string to set the `NSMicrophoneUsageDescription` permission message. |
| `colors` | `undefined` | Only for: android. An object containing color properties for customizing the image picker crop UI in light mode. |
| `colors.cropToolbarColor` | `#00000000` | Only for: android. A hex color string for the crop toolbar background color. |
| `colors.cropToolbarIconColor` | `#ffffff` | Only for: android. A hex color string for the crop toolbar icon color. |
| `colors.cropToolbarActionTextColor` | `#ffffff` | Only for: android. A hex color string for the crop toolbar action text color. |
| `colors.cropBackButtonIconColor` | `#ffffff` | Only for: android. A hex color string for the crop toolbar back button icon color. |
| `colors.cropBackgroundColor` | `#ffffff` | Only for: android. A hex color string for the crop screen background color. |
| `dark.colors` | `{ cropToolbarColor: "#00000000", cropToolbarIconColor: "#ffffff", cropToolbarActionTextColor: "#ffffff", cropBackButtonIconColor: "#ffffff", cropBackgroundColor: "#000000"  }` | Only for: android. An object containing color properties for customizing the image picker crop UI in dark mode. |

<ConfigReactNative>

If you're not using Continuous Native Generation ([CNG](https://docs.expo.dev/workflow/continuous-native-generation/)) or you're using a native **ios** project manually, then you need to add `NSPhotoLibraryUsageDescription`, `NSCameraUsageDescription`, and `NSMicrophoneUsageDescription` keys to your **ios/[app]/Info.plist**:

```xml Info.plist
<key>NSPhotoLibraryUsageDescription</key>
<string>Give $(PRODUCT_NAME) permission to save photos</string>
<key>NSCameraUsageDescription</key>
<string>Give $(PRODUCT_NAME) permission to access your camera</string>
<key>NSMicrophoneUsageDescription</key>
<string>Give $(PRODUCT_NAME) permission to use your microphone</string>
```

</ConfigReactNative>

## Usage

```tsx
import { useState } from 'react';
import { Alert, Button, Image, View, StyleSheet } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

export default function ImagePickerExample() {
  const [image, setImage] = useState<string | null>(null);

  const pickImage = async () => {
    // No permissions request is necessary for launching the image library.
    // Manually request permissions for videos on iOS when `allowsEditing` is set to `false`
    // and `videoExportPreset` is `'Passthrough'` (the default), ideally before launching the picker
    // so the app users aren't surprised by a system dialog after picking a video.
    // See "Invoke permissions for videos" sub section for more details.
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!permissionResult.granted) {
      Alert.alert('Permission required', 'Permission to access the media library is required.');
      return;
    }

    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images', 'videos'],
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    console.log(result);

    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  return (
    <View style={styles.container}>
      <Button title="Pick an image from camera roll" onPress={pickImage} />
      {image && <Image source={{ uri: image }} style={styles.image} />}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  image: {
    width: 200,
    height: 200,
  },
});
```

When you run this example and pick an image, you will see the image that you picked show up in your app, and a similar log will be shown in the console:

```json collapseHeight=425
{
  "assets": [
    {
      "assetId": "C166F9F5-B5FE-4501-9531",
      "base64": null,
      "duration": null,
      "exif": null,
      "fileName": "IMG.HEIC",
      "fileSize": 6018901,
      "height": 3025,
      "type": "image",
      "uri": "file:///data/user/0/host.exp.exponent/cache/cropped1814158652.jpg"
      "width": 3024
    }
  ],
  "canceled": false
}
```

### Invoke permissions for videos <PlatformTags platforms={['ios']} />

In SDK 54 and later, the default configuration keeps `allowsEditing` set to `false` and [`videoExportPreset`](#videoexportpreset) set to `'Passthrough'`. These settings return the original asset (including HEIC and AVIF files) instantly because the picker skips compression, but iOS requires media library permission to access the original file and displays a permission dialog immediately after the user selects a video.

To avoid showing permissions dialog after selection, **manually request media library permissions before opening the picker** via [`requestMediaLibraryPermissionsAsync`](#imagepickerrequestmedialibrarypermissionsasyncwriteonly) or [`useMediaLibraryPermissions`](#usemedialibrarypermissionsoptions).

### With AWS S3

[AWS storage example](https://github.com/expo/examples/tree/master/with-aws-storage-upload)

See [Amplify documentation](https://docs.amplify.aws/) guide to set up your project correctly.

### With Firebase

[Firebase storage example](https://github.com/expo/examples/tree/master/with-firebase-storage-upload)

See [Using Firebase](https://docs.expo.dev/guides/using-firebase/) guide to set up your project correctly.

## API

```js
import * as ImagePicker from 'expo-image-picker';
```

## API: expo-image-picker

### Hooks

#### useCameraPermissions (*Function*)
Check or request permissions to access the camera.
This uses both `requestCameraPermissionsAsync` and `getCameraPermissionsAsync` to interact with the permissions.
- `useCameraPermissions(options?: PermissionHookOptions<object>): [null | PermissionResponse, RequestPermissionMethod<PermissionResponse>, GetPermissionMethod<PermissionResponse>]`
  Check or request permissions to access the camera.
  This uses both `requestCameraPermissionsAsync` and `getCameraPermissionsAsync` to interact with the permissions.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `options` *(optional)* | PermissionHookOptions<object> | - |
  Example:
  ```ts
  const [status, requestPermission] = ImagePicker.useCameraPermissions();
  ```

#### useMediaLibraryPermissions (*Function*)
Check or request permissions to access the media library.
This uses both `requestMediaLibraryPermissionsAsync` and `getMediaLibraryPermissionsAsync` to interact with the permissions.
- `useMediaLibraryPermissions(options?: PermissionHookOptions<{ writeOnly: boolean }>): [null | MediaLibraryPermissionResponse, RequestPermissionMethod<MediaLibraryPermissionResponse>, GetPermissionMethod<MediaLibraryPermissionResponse>]`
  Check or request permissions to access the media library.
  This uses both `requestMediaLibraryPermissionsAsync` and `getMediaLibraryPermissionsAsync` to interact with the permissions.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `options` *(optional)* | PermissionHookOptions<{ writeOnly: boolean }> | - |
  Example:
  ```ts
  const [status, requestPermission] = ImagePicker.useMediaLibraryPermissions();
  ```

### ImagePicker Methods

#### getCameraPermissionsAsync (*Function*)
- `getCameraPermissionsAsync(): Promise<CameraPermissionResponse>`
  Checks user's permissions for accessing camera.
  Returns: A promise that fulfills with an object of type [CameraPermissionResponse](#camerapermissionresponse).

#### getMediaLibraryPermissionsAsync (*Function*)
- `getMediaLibraryPermissionsAsync(writeOnly: boolean): Promise<MediaLibraryPermissionResponse>`
  Checks user's permissions for accessing photos.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `writeOnly` | boolean | Whether to request write or read and write permissions. Defaults to `false` |
  Returns: A promise that fulfills with an object of type [MediaLibraryPermissionResponse](#medialibrarypermissionresponse).

#### getPendingResultAsync (*Function*)
- `getPendingResultAsync(): Promise<ImagePickerResult | ImagePickerErrorResult | null>`
  Android system sometimes kills the `MainActivity` after the `ImagePicker` finishes. When this
  happens, we lose the data selected using the `ImagePicker`. However, you can retrieve the lost
  data by calling `getPendingResultAsync`. You can test this functionality by turning on
  `Don't keep activities` in the developer options.
  Returns: - **On Android:** a promise that resolves to an object of exactly same type as in
  `ImagePicker.launchImageLibraryAsync` or `ImagePicker.launchCameraAsync` if the `ImagePicker`
  finished successfully. Otherwise, an object of type [`ImagePickerErrorResult`](#imagepickerimagepickererrorresult).
  - **On other platforms:** `null`

#### launchCameraAsync (*Function*)
- `launchCameraAsync(options: ImagePickerOptions): Promise<ImagePickerResult>`
  Display the system UI for taking a photo with the camera. Requires `Permissions.CAMERA`.
  On Android and iOS 10 `Permissions.CAMERA_ROLL` is also required. On mobile web, this must be
  called immediately in a user interaction like a button press, otherwise the browser will block
  the request without a warning.
  > **Note:** Make sure that you handle `MainActivity` destruction on **Android**. See [ImagePicker.getPendingResultAsync](#imagepickergetpendingresultasync).
  > **Notes for Web:** The system UI can only be shown after user activation (e.g. a `Button` press).
  Therefore, calling `launchCameraAsync` in `componentDidMount`, for example, will **not** work as
  intended. The `cancelled` event will not be returned in the browser due to platform restrictions
  and inconsistencies across browsers.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `options` | ImagePickerOptions | An `ImagePickerOptions` object. |
  Returns: A promise that resolves to an object with `canceled` and `assets` fields.
  When the user canceled the action the `assets` is always `null`, otherwise it's an array of
  the selected media assets which have a form of [`ImagePickerAsset`](#imagepickerasset).

#### launchImageLibraryAsync (*Function*)
- `launchImageLibraryAsync(options: ImagePickerOptions): Promise<ImagePickerResult>`
  Display the system UI for choosing an image or a video from the phone's library.
  Requires `Permissions.MEDIA_LIBRARY` on iOS 10 only. On mobile web, this must be     called
  immediately in a user interaction like a button press, otherwise the browser will block the
  request without a warning.

  **Animated GIFs support:** On Android, if the selected image is an animated GIF, the result image will be an
  animated GIF too if and only if `quality` is explicitly set to `1.0` and `allowsEditing` is set to `false`.
  Otherwise compression and/or cropper will pick the first frame of the GIF and return it as the
  result (on Android the result will be a PNG). On iOS, both quality and cropping are supported.

  > **Notes for Web:** The system UI can only be shown after user activation (e.g. a `Button` press).
  Therefore, calling `launchImageLibraryAsync` in `componentDidMount`, for example, will **not**
  work as intended. The `cancelled` event will not be returned in the browser due to platform
  restrictions and inconsistencies across browsers.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `options` | ImagePickerOptions | An object extended by [`ImagePickerOptions`](#imagepickeroptions). |
  Returns: A promise that resolves to an object with `canceled` and `assets` fields.
  When the user canceled the action the `assets` is always `null`, otherwise it's an array of
  the selected media assets which have a form of [`ImagePickerAsset`](#imagepickerasset).

#### requestCameraPermissionsAsync (*Function*)
- `requestCameraPermissionsAsync(): Promise<CameraPermissionResponse>`
  Asks the user to grant permissions for accessing camera. This does nothing on web because the
  browser camera is not used.
  Returns: A promise that fulfills with an object of type [CameraPermissionResponse](#camerarollpermissionresponse).

#### requestMediaLibraryPermissionsAsync (*Function*)
- `requestMediaLibraryPermissionsAsync(writeOnly: boolean): Promise<MediaLibraryPermissionResponse>`
  Asks the user to grant permissions for accessing user's photo. This method does nothing on web.
  | Parameter | Type | Description |
  | --- | --- | --- |
  | `writeOnly` | boolean | Whether to request write or read and write permissions. Defaults to `false` |
  Returns: A promise that fulfills with an object of type [MediaLibraryPermissionResponse](#medialibrarypermissionresponse).

### Types

#### CameraPermissionResponse (*Type*)
Alias for `PermissionResponse` type exported by `expo-modules-core`.
Type: PermissionResponse

#### CropShape (*Type*)
The shape of the crop area.
Type: 'rectangle' | 'oval'

#### DefaultTab (*Type*)
The default tab with which the image picker will be opened.
- `'photos'` - the photos/videos tab will be opened.
- `'albums'` - the albums tab will be opened.
Available on platform: android
Type: 'photos' | 'albums'

#### ImagePickerAsset (*Type*)
Represents an asset (image or video) returned by the image picker or camera.
| Property | Type | Description |
| --- | --- | --- |
| `assetId` *(optional)* | string \| null | The unique ID that represents the picked image or video, if picked from the library. It can be used<br>by [expo-media-library](./media-library) to manage the picked asset.<br><br>> This might be `null` when the ID is unavailable or the user gave limited permission to access the media library.<br>> On Android, the ID is unavailable when the user selects a photo by directly browsing file system. Available on platforms: android, ios |
| `base64` *(optional)* | string \| null | When the `base64` option is truthy, it is a Base64-encoded string of the selected image's JPEG data, otherwise `null`.<br>If you prepend this with `'data:image/jpeg;base64,'` to create a data URI,<br>you can use it as the source of an `Image` element; for example:<br>```ts<br><Image<br>  source={{ uri: 'data:image/jpeg;base64,' + asset.base64 }}<br>  style={{ width: 200, height: 200 }}<br>/><br>``` |
| `duration` *(optional)* | number \| null | Length of the video in milliseconds or `null` if the asset is not a video. |
| `exif` *(optional)* | Record<string, any> \| null | The `exif` field is included if the `exif` option is truthy, and is an object containing the<br>image's EXIF data. The names of this object's properties are EXIF tags and the values are the<br>respective EXIF values for those tags. Available on platforms: android, ios |
| `file` *(optional)* | File | The web `File` object containing the selected media. This property is web-only and can be used to upload to a server with `FormData`. Available on platform: web |
| `fileName` *(optional)* | string \| null | Preferred filename to use when saving this item. This might be `null` when the name is unavailable<br>or user gave limited permission to access the media library. |
| `fileSize` *(optional)* | number | File size of the picked image or video, in bytes. |
| `height` | number | Height of the image or video. |
| `mimeType` *(optional)* | string | The MIME type of the selected asset or `null` if could not be determined. |
| `pairedVideoAsset` *(optional)* | ImagePickerAsset \| null | Contains information about the video paired with the image file. This property is only set when `livePhotos` media type was present in the `mediaTypes` array when launching the picker and a live photo was selected. Available on platform: ios |
| `type` *(optional)* | 'image' \| 'video' \| 'livePhoto' \| 'pairedVideo' | The type of the asset.<br>- `'image'` - for images.<br>- `'video'` - for videos.<br>- `'livePhoto'` - for live photos. (iOS only)<br>- `'pairedVideo'` - for videos paired with photos, which can be combined to create a live photo. (iOS only) |
| `uri` | string | URI to the local image or video file (usable as the source of an `Image` element, in the case of<br>an image) and `width` and `height` specify the dimensions of the media. |
| `width` | number | Width of the image or video. |

#### ImagePickerCanceledResult (*Type*)
Type representing canceled pick result.
| Property | Type | Description |
| --- | --- | --- |
| `assets` | null | `null` signifying that the request was canceled. |
| `canceled` | true | Boolean flag set to `true` showing that the request was canceled. |

#### ImagePickerErrorResult (*Type*)
| Property | Type | Description |
| --- | --- | --- |
| `code` | string | The error code. |
| `exception` *(optional)* | string | The exception which caused the error. |
| `message` | string | The error message. |

#### ImagePickerOptions (*Type*)
| Property | Type | Description |
| --- | --- | --- |
| `allowsEditing` *(optional)* | boolean | Whether to show a UI to edit the image after it is picked. On Android the user can crop and<br>rotate the image and on iOS simply crop it.<br><br>> - Cropping multiple images is not supported - this option is mutually exclusive with `allowsMultipleSelection`.<br>> - On iOS, this option is ignored if `allowsMultipleSelection` is enabled.<br>> - On iOS cropping a `.bmp` image will convert it to `.png`. Default: `false` Available on platforms: android, ios |
| `allowsMultipleSelection` *(optional)* | boolean | Whether or not to allow selecting multiple media files at once.<br><br>> Cropping multiple images is not supported - this option is mutually exclusive with `allowsEditing`.<br>> If this option is enabled, then `allowsEditing` is ignored. Default: `false` Available on platforms: android, ios 14+, web |
| `aspect` *(optional)* | [number, number] | An array with two entries `[x, y]` specifying the aspect ratio to maintain if the user is<br>allowed to edit the image (by passing `allowsEditing: true`). This is only applicable on<br>Android, since on iOS the crop rectangle is always a square. |
| `base64` *(optional)* | boolean | Whether to also include the image data in Base64 format. |
| `cameraType` *(optional)* | CameraType | Selects the camera-facing type. The `CameraType` enum provides two options:<br>`front` for the front-facing camera and `back` for the back-facing camera.<br>- **On Android**, the behavior of this option may vary based on the camera app installed on the device.<br>- **On Web**, if this option is not provided, use "camera" as the default value of internal input element for backwards compatibility. Default: `CameraType.back` |
| `defaultTab` *(optional)* | DefaultTab | Choose the default tab with which the image picker will be opened. Default: `'photos'` Available on platform: android |
| `exif` *(optional)* | boolean | Whether to also include the EXIF data for the image. On iOS the EXIF data does not include GPS<br>tags in the camera case. Available on platforms: android, ios |
| `legacy` *(optional)* | boolean | Uses the legacy image picker on Android. This will allow media to be selected from outside the users photo library. Default: `false` Available on platform: android |
| `mediaTypes` *(optional)* | MediaType \| MediaType[] \| MediaTypeOptions | Choose what type of media to pick. Default: `'images'` |
| `orderedSelection` *(optional)* | boolean | Whether to display number badges when assets are selected. The badges are numbered<br>in selection order. Assets are then returned in the exact same order they were selected.<br><br>> Assets should be returned in the selection order regardless of this option,<br>> but there is no guarantee that it is always true when this option is disabled. Default: `false` Available on platform: ios 15+ |
| `preferredAssetRepresentationMode` *(optional)* | UIImagePickerPreferredAssetRepresentationMode | Choose [preferred asset representation mode](https://developer.apple.com/documentation/photokit/phpickerconfigurationassetrepresentationmode)<br>to use when loading assets. Default: `ImagePicker.UIImagePickerPreferredAssetRepresentationMode.Automatic` Available on platform: ios 14+ |
| `presentationStyle` *(optional)* | UIImagePickerPresentationStyle | Choose [presentation style](https://developer.apple.com/documentation/uikit/uiviewcontroller/1621355-modalpresentationstyle?language=objc)<br>to customize view during taking photo/video. Default: `ImagePicker.UIImagePickerPresentationStyle.Automatic` Available on platform: ios |
| `quality` *(optional)* | number | Specify the quality of compression, from `0` to `1`. `0` means compress for small size,<br>`1` means compress for maximum quality.<br>> Note: If the selected image has been compressed before, the size of the output file may be<br>> bigger than the size of the original image.<br><br>> Note: On iOS, if a `.bmp` or `.png` image is selected from the library, this option is ignored. Default: `1.0` Available on platforms: android, ios |
| `selectionLimit` *(optional)* | number | The maximum number of items that user can select. Applicable when `allowsMultipleSelection` is enabled.<br>Setting the value to `0` sets the selection limit to the maximum that the system supports. Default: `0` Available on platforms: android, ios 14+ |
| `shape` *(optional)* | CropShape | Specify the shape of the crop area if the user is allowed to edit the image<br>(by passing `allowsEditing: true`). This option is only applicable on Android. Default: `rectangle` Available on platform: android |
| `videoExportPreset` *(optional)* | VideoExportPreset | Specify preset which will be used to compress selected video. Default: `ImagePicker.VideoExportPreset.Passthrough` Available on platform: ios 11+ |
| `videoMaxDuration` *(optional)* | number | Maximum duration, in seconds, for video recording. Setting this to `0` disables the limit.<br>Defaults to `0` (no limit).<br>- **On iOS**, when `allowsEditing` is set to `true`, maximum duration is limited to 10 minutes.<br>  This limit is applied automatically, if `0` or no value is specified.<br>- **On Android**, effect of this option depends on support of installed camera app.<br>- **On Web** this option has no effect - the limit is browser-dependant. |
| `videoQuality` *(optional)* | UIImagePickerControllerQualityType | Specify the quality of recorded videos. Defaults to the highest quality available for the device. Default: `ImagePicker.UIImagePickerControllerQualityType.High` Available on platform: ios |

#### ImagePickerResult (*Type*)
Type representing successful and canceled pick result.
Type: ImagePickerSuccessResult | ImagePickerCanceledResult

#### ImagePickerSuccessResult (*Type*)
Type representing successful pick result.
| Property | Type | Description |
| --- | --- | --- |
| `assets` | ImagePickerAsset[] | An array of picked assets. |
| `canceled` | false | Boolean flag set to `false` showing that the request was successful. |

#### MediaLibraryPermissionResponse (*Type*)
Extends `PermissionResponse` type exported by `expo-modules-core`, containing additional iOS-specific field.
| Property | Type | Description |
| --- | --- | --- |
| `accessPrivileges` *(optional)* | 'all' \| 'limited' \| 'none' | Indicates if your app has access to the whole or only part of the photo library. Possible values are:<br>- `'all'` if the user granted your app access to the whole photo library<br>- `'limited'` if the user granted your app access only to selected photos (only available on Android API 34+ and iOS 14.0+)<br>- `'none'` if user denied or hasn't yet granted the permission |

#### MediaType (*Type*)
Media types that can be picked by the image picker.
- `'images'` - for images.
- `'videos'` - for videos.
- `'livePhotos'` - for live photos (iOS only).

> When the `livePhotos` type is added to the media types array and a live photo is selected,
> the resulting `ImagePickerAsset` will contain an unaltered image and the `pairedVideoAsset` field will contain a
> video asset paired with the image. This option will be ignored when the `allowsEditing` option is enabled. Due
> to platform limitations live photos are returned at original quality, regardless of the `quality` option.

> When on Android or Web `livePhotos` type passed as a media type will be ignored.
Type: 'images' | 'videos' | 'livePhotos'

#### PermissionExpiration (*Type*)
Permission expiration time. Currently, all permissions are granted permanently.
Type: 'never' | number

#### PermissionHookOptions (*Type*)
Type: PermissionHookBehavior & Options

#### PermissionResponse (*Type*)
An object obtained by permissions get and request functions.
| Property | Type | Description |
| --- | --- | --- |
| `canAskAgain` | boolean | Indicates if user can be asked again for specific permission.<br>If not, one should be directed to the Settings app<br>in order to enable/disable the permission. |
| `expires` | PermissionExpiration | Determines time when the permission expires. |
| `granted` | boolean | A convenience boolean that indicates if the permission is granted. |
| `status` | PermissionStatus | Determines the status of the permission. |

### Enums

#### CameraType (*Enum*)
#### Members
- `back` — Back/rear camera.
- `front` — Front camera

#### MediaTypeOptions (*Enum*)
#### Members
- `All` — Images and videos.
- `Images` — Only images.
- `Videos` — Only videos.

#### PermissionStatus (*Enum*)
#### Members
- `DENIED` — User has denied the permission.
- `GRANTED` — User has granted the permission.
- `UNDETERMINED` — User hasn't granted or denied the permission yet.

#### UIImagePickerControllerQualityType (*Enum*)
#### Members
- `High` — Highest available resolution.
- `IFrame1280x720` — 1280 × 720
- `IFrame960x540` — 960 × 540
- `Low` — Depends on the device.
- `Medium` — Depends on the device.
- `VGA640x480` — 640 × 480

#### UIImagePickerPreferredAssetRepresentationMode (*Enum*)
Picker preferred asset representation mode. Its values are directly mapped to the [`PHPickerConfigurationAssetRepresentationMode`](https://developer.apple.com/documentation/photokit/phpickerconfigurationassetrepresentationmode).
Available on platform: ios
#### Members
- `Automatic` — A mode that indicates that the system chooses the appropriate asset representation.
- `Compatible` — A mode that uses the most compatible asset representation.
- `Current` — A mode that uses the current representation to avoid transcoding, if possible.

#### UIImagePickerPresentationStyle (*Enum*)
Picker presentation style. Its values are directly mapped to the [`UIModalPresentationStyle`](https://developer.apple.com/documentation/uikit/uiviewcontroller/1621355-modalpresentationstyle).
Available on platform: ios
#### Members
- `AUTOMATIC` — The default presentation style chosen by the system.
On older iOS versions, falls back to `WebBrowserPresentationStyle.FullScreen`.
- `CURRENT_CONTEXT` — A presentation style where the picker is displayed over the app's content.
- `FORM_SHEET` — A presentation style that displays the picker centered in the screen.
- `FULL_SCREEN` — A presentation style in which the presented picker covers the screen.
- `OVER_CURRENT_CONTEXT` — A presentation style where the picker is displayed over the app's content.
- `OVER_FULL_SCREEN` — A presentation style in which the picker view covers the screen.
- `PAGE_SHEET` — A presentation style that partially covers the underlying content.
- `POPOVER` — A presentation style where the picker is displayed in a popover view.

#### VideoExportPreset (*Enum*)
#### Members
- `H264_1280x720` — Resolution: __1280 × 720__ •
Video compression: __H.264__ •
Audio compression: __AAC__
- `H264_1920x1080` — Resolution: __1920 × 1080__ •
Video compression: __H.264__ •
Audio compression: __AAC__
- `H264_3840x2160` — Resolution: __3840 × 2160__ •
Video compression: __H.264__ •
Audio compression: __AAC__
- `H264_640x480` — Resolution: __640 × 480__ •
Video compression: __H.264__ •
Audio compression: __AAC__
- `H264_960x540` — Resolution: __960 × 540__ •
Video compression: __H.264__ •
Audio compression: __AAC__
- `HEVC_1920x1080` — Resolution: __1920 × 1080__ •
Video compression: __HEVC__ •
Audio compression: __AAC__
- `HEVC_3840x2160` — Resolution: __3840 × 2160__ •
Video compression: __HEVC__ •
Audio compression: __AAC__
- `HighestQuality` — Resolution: __Depends on the device__ •
Video compression: __H.264__ •
Audio compression: __AAC__
- `LowQuality` — Resolution: __Depends on the device__ •
Video compression: __H.264__ •
Audio compression: __AAC__
- `MediumQuality` — Resolution: __Depends on the device__ •
Video compression: __H.264__ •
Audio compression: __AAC__
- `Passthrough` — Resolution: __Unchanged__ •
Video compression: __None__ •
Audio compression: __None__

## Permissions

### Android

The following permissions are added automatically through the library's **AndroidManifest.xml**.

<AndroidPermissions permissions={['CAMERA', 'READ_EXTERNAL_STORAGE', 'WRITE_EXTERNAL_STORAGE']} />

### iOS

The following usage description keys are used by the APIs in this library.

<IOSPermissions
  permissions={[
    'NSMicrophoneUsageDescription',
    'NSPhotoLibraryUsageDescription',
    'NSCameraUsageDescription',
  ]}
/>