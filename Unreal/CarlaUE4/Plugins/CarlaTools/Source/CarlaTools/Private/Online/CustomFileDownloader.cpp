// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de Barcelona (UAB). This work is licensed under the terms of the MIT license. For a copy, see <https://opensource.org/licenses/MIT>.

#undef CreateDirectory

#include "Online/CustomFileDownloader.h"
#include "OpenDriveToMap.h"
#include "HttpModule.h"
#include "Http.h"
#include "Misc/FileHelper.h"
#include "EditorUtilitySubsystem.h"

#include "Regex.h"
#include <iostream>
#include <fstream>
#include <string>
#include <regex>
#include "Containers/StringConv.h" 
#include "Regex.h"  
#include "Logging/LogMacros.h"
#include <random>

#include <OSM2ODR.h>

///https://portal.opentopography.org/API/globaldem?demtype=NASADEM&south=45.196&north=49&west=-122.66&east=-119.95&outputFormat=GTiff&API_Key=d54b0fdd6de0f7a46aa17d4a0a9b8624

void UCustomFileDownloader::SetRemovalPercentage(float Percentage)
{
    UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("custom file Percentage Set to value: %f"), Percentage);
    RemovalPercentage = Percentage;
}

void UCustomFileDownloader::BuildSetMinHeight(float InMinHeight)
{
    UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("Min Height Set to value: %f"), InMinHeight);
    MinHeight = InMinHeight;
}

void UCustomFileDownloader::BuildSetMaxHeight(float InMaxHeight)
{
    UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("Max Height Set to value: %f"), InMaxHeight);
    MaxHeight = InMaxHeight;
}

void UCustomFileDownloader::SetMinLevel(float InMinLevel)
{
    UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("Min Level Set to value: %f"), InMinLevel);
    MinLevel = InMinLevel;
}

void UCustomFileDownloader::SetMaxLevel(float InMaxLevel)
{
    UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("Max Level Set to value: %f"), InMaxLevel);
    MaxLevel = InMaxLevel;
}

std::string regex_escape(const std::string& str)
{
    static const std::regex specialChars(R"([.^$|()\\[*+?{}])");
    return std::regex_replace(str, specialChars, R"(\$&)");
}

std::string UCustomFileDownloader::PreProcess(const std::string& content)
{
    std::string result = editBuildingAmount(content);
    result = editBuildingHeights(result, MinHeight, MaxHeight);
    result = editBuildingLevels(result, MinLevel, MaxLevel);


    return content;
}

std::string UCustomFileDownloader::editElevation(const std::string& content)
{
    std::string elevationPattern = R"elevation(<elevation\s+s="([\d\.]+)"\s+a="([\d\.\-]+)"\s+b="([\d\.\-]+)"\s+c="([\d\.\-]+)"\s+d="([\d\.\-]+)"[^>]*>)elevation";

    std::regex elevationRegex(elevationPattern, std::regex_constants::ECMAScript | std::regex_constants::icase);

    std::ostringstream outputBuffer;
    size_t lastPos = 0;

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> slopeDist(-0.001, 0.001);  // slope between needs to be way less than .02 add input limits in later

    auto it = std::sregex_iterator(content.begin(), content.end(), elevationRegex);
    auto end = std::sregex_iterator();

    for (; it != end; ++it)
    {
        std::smatch match = *it;

        float s = std::stof(match.str(1));
        float a = std::stof(match.str(2));
        float b = std::stof(match.str(3));
        float c = std::stof(match.str(4));
        float d = std::stof(match.str(5));

        // Apply slope
        float newA = a + slopeDist(gen);
        float newB = b + slopeDist(gen);

        std::string adjustedTag = "<elevation s=\"" + std::to_string(s) +
            "\" a=\"" + std::to_string(newA) +
            "\" b=\"" + std::to_string(newB) +
            "\" c=\"" + std::to_string(c) +
            "\" d=\"" + std::to_string(d) + "\"/>";

        outputBuffer << content.substr(lastPos, match.position() - lastPos);

        outputBuffer << adjustedTag;

        lastPos = match.position() + match.length();
    }

    outputBuffer << content.substr(lastPos);

    return outputBuffer.str();
}

std::string UCustomFileDownloader::editBuildingAmount(const std::string& content)
{   
    UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("Editing buildings with Percentage value: %f"), RemovalPercentage);

    if (content.empty())
    {
        UE_LOG(LogCarlaToolsMapGenerator, Error, TEXT("Content is empty, skipping regex."));
        return content;
    }

    if (RemovalPercentage == 0)
    {
        return content;  // No changes needed if percentage is 0
    }

    // Validate RemovalPercentage
    if (RemovalPercentage < 0 || RemovalPercentage > 1)
    {
        UE_LOG(LogCarlaToolsMapGenerator, Error, TEXT("Invalid RemovalPercentage: %f"), RemovalPercentage);
        return content;
    }

    std::vector<std::string> buildingList;

    try
    {
        std::string buildingTagPattern = R"(<tag k="building"[^>]*>)";

        std::regex WayAndRelationWithBuildingTagPattern(buildingTagPattern, std::regex_constants::ECMAScript | std::regex_constants::icase);
        auto it = std::sregex_iterator(content.begin(), content.end(), WayAndRelationWithBuildingTagPattern);
        auto end = std::sregex_iterator();

        // Create building list
        for (; it != end; ++it)
        {
            buildingList.push_back(it->str());
        }
    }
    catch (const std::regex_error& e)
    {
        UE_LOG(LogCarlaToolsMapGenerator, Error, TEXT("Regex error: %s"), *FString(e.what()));
        return content;
    }

    // Check if we have any buildings to process
    if (buildingList.empty())
    {
        UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("No buildings found in the content."));
        return content;
    }

    int totalBuildings = buildingList.size();
    int buildingsToRemove = static_cast<int>(totalBuildings * (1-RemovalPercentage));

    // Shuffle building list to remove randomly
    std::random_device rd;
    std::mt19937 gen(rd());
    std::shuffle(buildingList.begin(), buildingList.end(), gen);

    std::string result = content;

    // Remove the buildings
    for (int i = 0; i < buildingsToRemove; ++i)
    {
        try
        {
            result = std::regex_replace(result, std::regex(regex_escape(buildingList[i])), "");
        }
        catch (const std::regex_error& e)
        {
            UE_LOG(LogCarlaToolsMapGenerator, Error, TEXT("Regex replacement error: %s"), *FString(e.what()));
            return result;  // Return current result if replacement fails
        }
    }

    return result;
}


std::string UCustomFileDownloader::editBuildingLevels(const std::string& content, int minLevels, int maxLevels)
{
    int buildingHeightMultiplier = 1;
   
    std::string buildingLevelsPattern = "<tag k=\"building:levels\" v=\"(\\d+)\"[^>]*>";

    // find all <tag k="building:levels" v="X"/> elements
    std::regex levelsPattern(buildingLevelsPattern, std::regex_constants::ECMAScript | std::regex_constants::icase);

    // Use a regex iterator to collect all matches
    std::string result = content;
    auto it = std::sregex_iterator(result.begin(), result.end(), levelsPattern);
    auto end = std::sregex_iterator();

    for (; it != end; ++it)
    {
        // Extract the current number of levels
        std::string matchedTag = it->str();
        int currentLevel = std::stoi(it->str(1));

        currentLevel *= buildingHeightMultiplier;

        int adjustedLevel = std::max(currentLevel, minLevels);

        
        if (maxLevels > 0)
        {
            adjustedLevel = std::min(adjustedLevel, maxLevels);
        }

        // level adjustment
        //int adjustedLevel = std::min(std::max(currentLevel, minLevels), maxLevels);

        std::string adjustedTag = "<tag k=\"building:levels\" v=\"" + std::to_string(adjustedLevel) + "\"/>";

        // Replace the original tag with the adjusted tag
        result.replace(it->position(), it->length(), adjustedTag);
    }

    return result;
}

std::string UCustomFileDownloader::editLanes(const std::string& content, float minLanes, float maxLanes)
{
    std::string lanePattern = "<tag k=\"lanes\" v=\"([\\d\\.]+)\"[^>]*>"; 

    // Use regex to find all <tag k="lanes" v="X"/> elements
    std::regex laneRegex(lanePattern, std::regex_constants::ECMAScript | std::regex_constants::icase);

    std::ostringstream outputBuffer;
    size_t lastPos = 0;

    auto it = std::sregex_iterator(content.begin(), content.end(), laneRegex);
    auto end = std::sregex_iterator();

    for (; it != end; ++it)
    {
        std::smatch match = *it;

        // Extract the current lane value
        std::string matchedTag = match.str();
        float currentLanes = std::stof(match.str(1));

        // Adjust the lanes
        float adjustedLanes = std::min(std::max(currentLanes, minLanes), maxLanes);

        std::string adjustedTag = "<tag k=\"lanes\" v=\"" + std::to_string(adjustedLanes) + "\"/>";

        outputBuffer << content.substr(lastPos, match.position() - lastPos);
        outputBuffer << adjustedTag;

        lastPos = match.position() + match.length();
    }

    outputBuffer << content.substr(lastPos);

    return outputBuffer.str();
}

std::string UCustomFileDownloader::editBuildingHeights(const std::string& content, float minHeight, float maxHeight)
{
    int buildingHeightMultiplier = 1;
   
    std::string heightPattern = "<tag k=\"height\" v=\"([\\d\\.]+)\"[^>]*>";

    std::regex heightRegex(heightPattern, std::regex_constants::ECMAScript | std::regex_constants::icase);

    std::ostringstream outputBuffer;
    size_t lastPos = 0;

    auto it = std::sregex_iterator(content.begin(), content.end(), heightRegex);
    auto end = std::sregex_iterator();

    for (; it != end; ++it)
    {
        std::smatch match = *it;

        std::string matchedTag = match.str();
        float currentHeight = std::stof(match.str(1));  

        currentHeight *= buildingHeightMultiplier;

        
        float adjustedHeight = std::max(currentHeight, minHeight);

        if (maxHeight > 0)
        {
            adjustedHeight = std::min(adjustedHeight, maxHeight);
        }

 
        std::string adjustedTag = "<tag k=\"height\" v=\"" + std::to_string(adjustedHeight) + "\"/>";

        outputBuffer << content.substr(lastPos, match.position() - lastPos);

        outputBuffer << adjustedTag;

        
        lastPos = match.position() + match.length();
    }

    outputBuffer << content.substr(lastPos);

    return outputBuffer.str();
}


void UCustomFileDownloader::ConvertOSMInOpenDrive(FString FilePath, float Lat_0, float Lon_0)
{
    IPlatformFile& FileManager = FPlatformFileManager::Get().GetPlatformFile();
    FString FileContent;

    // Check if the file exists
    if (!FileManager.FileExists(*FilePath))
    {
        UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("File: %s does not exist"), *FilePath);
        return;
    }

    // First, read and process the OSM content to OpenDRIVE
    if (FFileHelper::LoadFileToString(FileContent, *FilePath, FFileHelper::EHashOptions::None))
    {
        UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("FileManipulation: Loaded OSM file: %s"), *FilePath);
    }
    else
    {
        UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("FileManipulation: Failed to load OSM file"));
        return;
    }

    // Convert OSM to OpenDRIVE format
    std::string OsmFile = std::string(TCHAR_TO_UTF8(*FileContent));
    osm2odr::OSM2ODRSettings Settings;
    Settings.proj_string += " +lat_0=" + std::to_string(Lat_0) + " +lon_0=" + std::to_string(Lon_0);
    Settings.center_map = false;

    std::string OpenDriveFile = osm2odr::ConvertOSMToOpenDRIVE(OsmFile, Settings);

    // Save the OpenDRIVE output
    FilePath.RemoveFromEnd(".osm", ESearchCase::IgnoreCase);
    FilePath += ".xodr";

    if (FFileHelper::SaveStringToFile(FString(OpenDriveFile.c_str()), *FilePath))
    {
        UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("FileManipulation: Successfully Written: %s"), *FilePath);
    }
    else
    {
        UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("FileManipulation: Failed to write OpenDRIVE file."));
        return;
    }

    // Load the saved OSM file again to edit it
    FString SavedFilePath = FilePath;
    SavedFilePath.RemoveFromEnd(".xodr");
    SavedFilePath += ".osm";

    FString SavedFileContent;
    FString XodrFileContent;
    if (FFileHelper::LoadFileToString(SavedFileContent, *SavedFilePath, FFileHelper::EHashOptions::None))
    {
        std::string SavedFileContentStr = std::string(TCHAR_TO_UTF8(*SavedFileContent));
        SavedFileContentStr = PreProcess(SavedFileContentStr);
        //SavedFileContentStr = editLanes(SavedFileContentStr, 1, 1);

        // Save the edited OSM file
        if (FFileHelper::SaveStringToFile(FString(SavedFileContentStr.c_str()), *SavedFilePath))
        {
            UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("FileManipulation: Successfully edited and saved OSM file: %s"), *SavedFilePath);
        }
        else
        {
            UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("FileManipulation: Failed to save edited OSM file."));
        }
    }

    if (FFileHelper::LoadFileToString(XodrFileContent, *FilePath))
    {
        // Apply lane modification
        std::string XodrFileContentStr = std::string(TCHAR_TO_UTF8(*XodrFileContent));
        //XodrFileContentStr = editLanes(XodrFileContentStr, 1, 1);
        XodrFileContentStr = editElevation(XodrFileContentStr);
        // Save the modified OpenDRIVE file
        if (FFileHelper::SaveStringToFile(FString(XodrFileContentStr.c_str()), *FilePath))
        {
            UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("Successfully edited and saved OpenDRIVE file: %s"), *FilePath);
        }
        else
        {
            UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("Failed to save modified OpenDRIVE file"));
        }
    }
    else
    {
        UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("FileManipulation: Failed to reload the saved OSM file."));
    }
}

void UCustomFileDownloader::StartDownload()
{

  UE_LOG(LogCarlaToolsMapGenerator, Log, TEXT("FHttpDownloader CREATED"));
  UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("Map Name Is %s"), *ResultFileName );
  FHttpDownloader *Download = new FHttpDownloader("GET", Url, ResultFileName, DownloadDelegate);
  Download->Run();
}

FHttpDownloader::FHttpDownloader(const FString &InVerb, const FString &InUrl, const FString &InFilename, FDownloadComplete &Delegate)
    : Verb(InVerb), Url(InUrl), Filename(InFilename), DelegateToCall(Delegate)
{
}

FHttpDownloader::FHttpDownloader()
{

}

void FHttpDownloader::Run(void)
{
  UE_LOG(LogCarlaToolsMapGenerator, Log, TEXT("Starting download [%s] Url=[%s]"), *Verb, *Url);
  TSharedPtr<IHttpRequest, ESPMode::ThreadSafe> Request = FHttpModule::Get().CreateRequest();
  UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("Map Name Is %s"), *Filename );
  Request->OnProcessRequestComplete().BindRaw(this, &FHttpDownloader::RequestComplete);
  Request->SetURL(Url);
  Request->SetVerb(Verb);
  Request->ProcessRequest();
}

void FHttpDownloader::RequestComplete(FHttpRequestPtr HttpRequest, FHttpResponsePtr HttpResponse, bool bSucceeded)
{
  if (!HttpResponse.IsValid() )
  {
    UE_LOG(LogCarlaToolsMapGenerator, Log, TEXT("Download failed. NULL response"));
  }
  else
  {
    // If we do not get success responses codes we do not do anything
    if (HttpResponse->GetResponseCode() < 200 || 300 <= HttpResponse->GetResponseCode())
    {
      UE_LOG(LogCarlaToolsMapGenerator, Error, TEXT("Error during download [%s] Url=[%s] Response=[%d]"),
             *HttpRequest->GetVerb(),
             *HttpRequest->GetURL(),
             HttpResponse->GetResponseCode());
      return;
    }

    UE_LOG(LogCarlaToolsMapGenerator, Log, TEXT("Completed download [%s] Url=[%s] Response=[%d]"),
           *HttpRequest->GetVerb(),
           *HttpRequest->GetURL(),
           HttpResponse->GetResponseCode());

    FString CurrentFile = FPaths::ProjectContentDir() + "CustomMaps/" + (Filename) + "/OpenDrive/";
    UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("FHttpDownloader::RequestComplete CurrentFile %s."), *CurrentFile);

    // We will use this FileManager to deal with the file.
    IPlatformFile &FileManager = FPlatformFileManager::Get().GetPlatformFile();
    if (!FileManager.DirectoryExists(*CurrentFile))
    {
      FileManager.CreateDirectory(*CurrentFile);
    }
    CurrentFile += Filename + ".osm";

    FString StringToWrite = HttpResponse->GetContentAsString();

    // We use the LoadFileToString to load the file into
    if (FFileHelper::SaveStringToFile(StringToWrite, *CurrentFile, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
    {
      UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("FileManipulation: Sucsesfuly Written "));
      DelegateToCall.ExecuteIfBound();
    }
    else
    {
      UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("FileManipulation: Failed to write FString to file."));
      UE_LOG(LogCarlaToolsMapGenerator, Warning, TEXT("FileManipulation: CurrentFile %s."), *CurrentFile);
    }
  }
  delete this;
}
