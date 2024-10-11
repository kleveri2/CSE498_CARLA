// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de Barcelona (UAB). This work is licensed under the terms of the MIT license. For a copy, see <https://opensource.org/licenses/MIT>.


#include "DebrisGenerationWidget.h"
#include "Engine/Engine.h"

#define DEBUG_MSG(x, ...) if(GEngine){GEngine->AddOnScreenDebugMessage(-1, 15.0f, FColor::Red, FString::Printf(TEXT(x), __VA_ARGS__));}

UDebrisGenerationWidget::UDebrisGenerationWidget()
{
}

UDebrisGenerationWidget::~UDebrisGenerationWidget()
{
}

void UDebrisGenerationWidget::Hello()
{
	DEBUG_MSG("Hello")
}

void UDebrisGenerationWidget::GenerateDebris()
{
	DEBUG_MSG("Generate Debris")
}

void UDebrisGenerationWidget::ClearDebris()
{
	DEBUG_MSG("Clear Debris")
}

UWorld* UDebrisGenerationWidget::MyGetWorld() {
    // https://stackoverflow.com/questions/58582638/get-game-state-inside-editor-widget-in-unreal-engine-4
    // Prefer PIE Worlds.
    // Fallback to Game Preview Worlds.
    // Ignore all other types (e.g., other preview worlds).

    UWorld* PIE = nullptr;
    UWorld* GamePreview = nullptr;

    for (FWorldContext const& Context : GEngine->GetWorldContexts())
    {
        switch (Context.WorldType)
        {
        case EWorldType::PIE:
            PIE = Context.World();
            break;
        case EWorldType::GamePreview:
            GamePreview = Context.World();
            break;
        }
    }

    if (PIE)
    {
        DEBUG_MSG("PIE")
        return PIE;
    }
    else if (GamePreview)
    {
        DEBUG_MSG("GamePreview")
        return GamePreview;
    }
    DEBUG_MSG("No world")
    return nullptr;
}