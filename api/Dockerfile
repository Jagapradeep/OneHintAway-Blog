# The API image, in three stages. Only the last one is shipped: the JDK, Maven and the
# source code stay behind in the earlier stages.
#
#   docker build -t onehintaway-api:local .        (run from api/)
#
# Tests are not run here: they need Docker themselves (Testcontainers). CI runs
# ./mvnw verify before any image is built.

# ---- 1. build: JDK + Maven wrapper -> the jar -------------------------------------------
FROM eclipse-temurin:21.0.13_9-jdk-noble AS build
WORKDIR /build

# Dependencies first, in their own layer. This layer is rebuilt only when pom.xml or the
# wrapper changes, so a code-only change reuses it and downloads nothing.
COPY .mvn/ .mvn/
COPY mvnw pom.xml ./
RUN chmod +x mvnw && ./mvnw --batch-mode --no-transfer-progress -q dependency:go-offline

# The code changes most often, so it comes last.
COPY src/ src/
RUN ./mvnw --batch-mode --no-transfer-progress -q package -DskipTests

# ---- 2. layers: split the jar into parts that change at different speeds ----------------
FROM eclipse-temurin:21.0.13_9-jre-alpine AS layers
WORKDIR /layers
COPY --from=build /build/target/*.jar application.jar
RUN java -Djarmode=tools -jar application.jar extract --layers --destination extracted

# ---- 3. runtime: a small JRE, the app, nothing else -------------------------------------
FROM eclipse-temurin:21.0.13_9-jre-alpine AS runtime

# Never run as root: a break-in through the app then has no rights over the container.
# A fixed number (not just a name) lets Kubernetes check it with runAsNonRoot later.
RUN addgroup -S -g 10001 app && adduser -S -u 10001 -G app app
WORKDIR /app

# Slowest-changing first: the libraries (about 80 MB) keep their layer from build to build;
# only the last, tiny layer holds our own classes.
COPY --from=layers /layers/extracted/dependencies/ ./
COPY --from=layers /layers/extracted/spring-boot-loader/ ./
COPY --from=layers /layers/extracted/snapshot-dependencies/ ./
COPY --from=layers /layers/extracted/application/ ./

USER 10001:10001
EXPOSE 8080

# The JVM sizes its heap from the container's memory limit, not the host's.
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75"

# Docker marks the container healthy only when the API says it can take traffic
# (the same endpoint Kubernetes will probe). busybox wget fails on any non-2xx answer.
HEALTHCHECK --interval=10s --timeout=3s --start-period=40s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/actuator/health/readiness || exit 1

# Exec form: java is process 1 and receives SIGTERM, so `docker stop` shuts down cleanly.
ENTRYPOINT ["java", "-jar", "application.jar"]
