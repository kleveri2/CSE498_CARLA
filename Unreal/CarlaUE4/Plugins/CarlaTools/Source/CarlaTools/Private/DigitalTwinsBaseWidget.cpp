// Copyright (c) 2023 Computer Vision Center (CVC) at the Universitat Autonoma
// de Barcelona (UAB).
//
// This work is licensed under the terms of the MIT license.
// For a copy, see <https://opensource.org/licenses/MIT>.

#include "DigitalTwinsBaseWidget.h"

#include "Blueprint/UserWidget.h"
#include "OpenDriveToMap.h"

static UOpenDriveToMap* OpenDriveToMapObject = nullptr;

UOpenDriveToMap* UDigitalTwinsBaseWidget::InitializeOpenDriveToMap(TSubclassOf<UOpenDriveToMap> BaseClass){

    if (OpenDriveToMapObject == nullptr && BaseClass != nullptr) {
        UE_LOG(LogCarlaTools, Error, TEXT("Creating New Object"));
        OpenDriveToMapObject = NewObject<UOpenDriveToMap>(this, BaseClass);
        PassDigitalTwinsBaseWidgetToOpenDrive(OpenDriveToMapObject);
    }
    return OpenDriveToMapObject;
}

UOpenDriveToMap* UDigitalTwinsBaseWidget::GetOpenDriveToMap(){
  return OpenDriveToMapObject;
}

void UDigitalTwinsBaseWidget::SetOpenDriveToMap(UOpenDriveToMap* ToSet){
  OpenDriveToMapObject = ToSet;
}

void UDigitalTwinsBaseWidget::DestroyOpenDriveToMap(){
  OpenDriveToMapObject->ConditionalBeginDestroy();
  OpenDriveToMapObject = nullptr;
}

void UDigitalTwinsBaseWidget::SetRemovalPercentage(float NewPercentage)
{
    RemovalPercentage = NewPercentage;
    UE_LOG(LogTemp, Warning, TEXT("Removal Percentage set to: %f"), RemovalPercentage);
}

void UDigitalTwinsBaseWidget::SetMinHeight(float InMinHeight)
{
    MinHeight = InMinHeight;
    UE_LOG(LogTemp, Warning, TEXT("Min Height set to: %f"), InMinHeight);
}

void UDigitalTwinsBaseWidget::SetMaxHeight(float InMaxHeight)
{
    MaxHeight = InMaxHeight;
    UE_LOG(LogTemp, Warning, TEXT("Max Height set to: %f"), InMaxHeight);
}

void UDigitalTwinsBaseWidget::SetMinLevel(float InMinLevel)
{
    MinLevel = InMinLevel;
    UE_LOG(LogTemp, Warning, TEXT("Min Level set to: %f"), InMinLevel);
}

void UDigitalTwinsBaseWidget::SetMaxLevel(float InMaxLevel)
{
    MaxLevel = InMaxLevel;
    UE_LOG(LogTemp, Warning, TEXT("Max Level set to: %f"), InMaxLevel);
}

float UDigitalTwinsBaseWidget::GetRemovalPercentage()
{
    UE_LOG(LogTemp, Warning, TEXT("Getting removal Percentage: %f"), RemovalPercentage);
    return RemovalPercentage;
}

void UDigitalTwinsBaseWidget::PassDigitalTwinsBaseWidgetToOpenDrive(UOpenDriveToMap* OpenDriveInstance)
{
    if (OpenDriveInstance)
    {
        OpenDriveInstance->SetDigitalTwinsBaseWidget(this);
        OpenDriveInstance->SetRemovalPercentage(RemovalPercentage);
        OpenDriveInstance->BuildSetMinHeight(MinHeight);
        OpenDriveInstance->BuildSetMaxHeight(MaxHeight);
        OpenDriveInstance->SetMinLevel(MinLevel);
        OpenDriveInstance->SetMaxLevel(MaxLevel);
        UE_LOG(LogTemp, Warning, TEXT("DigitalTwinsBaseWidget passed to OpenDriveToMap."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("OpenDriveToMap instance is null, cannot pass DigitalTwinsBaseWidget."));
    }
}