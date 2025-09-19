# Kotlin Multiplatform (default)

- Format: prefer Gradle task (`ktlintFormat` or `spotlessApply`); fallback `ktlint -F`
- Lint: prefer Gradle `detekt` task; optionally enforce ktlint via plugin
- Build/types: `./gradlew build` (consider `-Werror`), fix compiler warnings/errors
- Debug cleanup: remove `println`, `printStackTrace`, `TODO()`
